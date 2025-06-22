from app.agents.topic_extractor import TopicExtractorAgent
from app.agents.emotion_targeting import EmotionTargetingAgent
from app.agents.content_generator import ContentGeneratorAgent
from typing import Dict, List, Any, Optional, AsyncGenerator
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

load_dotenv()


class StreamingPipelineService:
    """
    Streaming service that processes content and yields posts as they're completed.
    
    Flow: Text → Topics → Enhanced Topics (with emotions) → Content (streamed as ready)
    """
    
    def __init__(self):
        # Initialize all three agents with configuration from environment
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
        temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.3"))
        
        self.topic_extractor = TopicExtractorAgent(
            model_name=model_name,
            temperature=0.1  # Lower temperature for topic extraction
        )
        
        self.emotion_analyzer = EmotionTargetingAgent(
            model_name=model_name,
            temperature=0.1  # Lower temperature for emotion analysis
        )
        
        self.content_generator = ContentGeneratorAgent(
            model_name=model_name,
            temperature=temperature  # Higher temperature for content generation
        )
    
    async def stream_posts(
        self,
        text: str,
        original_url: Optional[str] = None,
        target_platforms: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream social media posts as they're generated through the pipeline.
        
        Args:
            text: The original text to process
            original_url: URL of the original content (optional)
            target_platforms: List of target platforms (default: ["twitter"])
            
        Yields:
            SSE-formatted strings with post data or status updates
        """
        start_time = datetime.now()
        
        try:
            # Input validation
            if not text or not text.strip():
                yield self._format_sse_event("error", {"error": "Text cannot be empty"})
                return
            
            # Use empty string as default if no URL provided
            if not original_url:
                original_url = ""
            
            if target_platforms is None:
                target_platforms = ["twitter"]
            
            # Send initial status
            yield self._format_sse_event("status", {
                "message": "Starting pipeline...",
                "stage": "initialization",
                "progress": 0,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 1: Extract topics (0-25%)
            yield self._format_sse_event("status", {
                "message": "Extracting topics...",
                "stage": "topic_extraction",
                "progress": 5,
                "timestamp": datetime.now().isoformat()
            })
            
            topic_result = self.topic_extractor.extract_topics(text)
            
            if not topic_result['success']:
                yield self._format_sse_event("error", {
                    "error": f"Topic extraction failed: {topic_result['error']}",
                    "stage": "topic_extraction"
                })
                return
            
            if not topic_result['topics']:
                yield self._format_sse_event("error", {
                    "error": "No topics were extracted from the text",
                    "stage": "topic_extraction"
                })
                return
            
            topics_found = len(topic_result['topics'])
            yield self._format_sse_event("status", {
                "message": f"Found {topics_found} topics",
                "stage": "topic_extraction_complete",
                "topics_count": topics_found,
                "progress": 25,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 2: Analyze emotions for the extracted topics (25-50%)
            yield self._format_sse_event("status", {
                "message": "Analyzing emotions...",
                "stage": "emotion_analysis",
                "progress": 30,
                "timestamp": datetime.now().isoformat()
            })
            
            emotion_result = self.emotion_analyzer.analyze_emotions(topic_result['topics'])
            
            if not emotion_result['success']:
                yield self._format_sse_event("error", {
                    "error": f"Emotion analysis failed: {emotion_result['error']}",
                    "stage": "emotion_analysis"
                })
                return
            
            if not emotion_result['emotion_analysis']:
                yield self._format_sse_event("error", {
                    "error": "No emotion analysis results were generated",
                    "stage": "emotion_analysis"
                })
                return
            
            enhanced_topics = emotion_result['emotion_analysis']
            total_posts_expected = len(enhanced_topics) * len(target_platforms)
            
            yield self._format_sse_event("status", {
                "message": f"Emotion analysis complete. Generating {total_posts_expected} posts...",
                "stage": "content_generation_start",
                "total_posts_expected": total_posts_expected,
                "platforms": target_platforms,
                "progress": 50,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 3: Generate content in parallel and stream as completed
            async for event in self._stream_content_generation(
                enhanced_topics=enhanced_topics,
                original_text=text,
                original_url=original_url,
                target_platforms=target_platforms
            ):
                yield event
            
            # Send completion status
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            
            yield self._format_sse_event("complete", {
                "message": "All posts generated successfully!",
                "total_processing_time": total_processing_time,
                "progress": 100,
                "timestamp": end_time.isoformat()
            })
            
        except Exception as e:
            yield self._format_sse_event("error", {
                "error": f"Pipeline processing error: {str(e)}",
                "stage": "unknown"
            })
    
    async def _stream_content_generation(
        self,
        enhanced_topics: List[Dict[str, Any]],
        original_text: str,
        original_url: str,
        target_platforms: List[str]
    ) -> AsyncGenerator[str, None]:
        """
        Generate content for all topic/platform combinations in parallel
        and stream posts as they're completed.
        """
        # Create tasks for parallel execution
        tasks = []
        task_metadata = []  # To track which task corresponds to which topic/platform
        
        for topic in enhanced_topics:
            for platform in target_platforms:
                task = self._generate_single_post(
                    topic=topic,
                    original_text=original_text,
                    original_url=original_url,
                    platform=platform
                )
                tasks.append(task)
                metadata = {
                    'topic_id': topic['topic_id'],
                    'topic_name': topic['topic_name'],
                    'platform': platform
                }
                task_metadata.append(metadata)
                print(f"📝 Creating task for: {metadata}")  # Debug log
        
        # Process tasks as they complete
        posts_completed = 0
        total_posts = len(tasks)
        
                 # Execute all tasks in parallel and wait for results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results with correct metadata mapping
        for i, (result, metadata) in enumerate(zip(results, task_metadata)):
            posts_completed += 1
            
            # Handle exceptions
            if isinstance(result, Exception):
                yield self._format_sse_event("post_error", {
                    "error": f"Failed to generate post: {str(result)}",
                    "topic_id": metadata['topic_id'],
                    "topic_name": metadata['topic_name'],
                    "platform": metadata['platform'],
                    "progress": {
                        "completed": posts_completed,
                        "total": len(tasks)
                    },
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            if result['success']:
                # Calculate progress (50-100% for content generation)
                content_progress = 50 + (posts_completed / len(tasks)) * 50
                
                # Stream the completed post
                post_data = {
                    "post_content": result['final_post'],
                    "topic_id": metadata['topic_id'],
                    "topic_name": metadata['topic_name'],
                    "platform": metadata['platform'],
                    "primary_emotion": result.get('primary_emotion', ''),
                    "content_strategy": result['content_strategy'],
                    "processing_time": result['processing_time'],
                    "progress": round(content_progress),
                    "post_progress": {
                        "completed": posts_completed,
                        "total": len(tasks)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                print(f"🎉 Streaming post: {post_data['platform']} - {post_data['post_content'][:50]}...")  # Debug log
                yield self._format_sse_event("post", post_data)
            else:
                # Calculate progress even for errors
                content_progress = 50 + (posts_completed / len(tasks)) * 50
                
                # Stream error for this specific post
                yield self._format_sse_event("post_error", {
                    "error": result['error'],
                    "topic_id": metadata['topic_id'],
                    "topic_name": metadata['topic_name'],
                    "platform": metadata['platform'],
                    "progress": round(content_progress),
                    "post_progress": {
                        "completed": posts_completed,
                        "total": len(tasks)
                    },
                    "timestamp": datetime.now().isoformat()
                })
    
    async def _generate_single_post(
        self,
        topic: Dict[str, Any],
        original_text: str,
        original_url: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Generate content for a single topic/platform combination.
        Runs in thread pool to avoid blocking the event loop.
        """
        try:
            # Run the synchronous agent method in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    self.content_generator.generate_content_for_topic,
                    topic,
                    original_text,
                    original_url,
                    platform
                )
            
            # Add topic information to result
            result['primary_emotion'] = topic.get('primary_emotion', '')
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to generate content: {str(e)}",
                'final_post': "",
                'content_strategy': "",
                'processing_time': 0.0,
                'primary_emotion': topic.get('primary_emotion', '')
            }
    
    def _format_sse_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Format data as Server-Sent Event.
        
        Args:
            event_type: Type of event (status, post, error, complete)
            data: Event data
            
        Returns:
            SSE-formatted string
        """
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


class StreamingPipelineError(Exception):
    """Custom exception for streaming pipeline errors"""
    pass 