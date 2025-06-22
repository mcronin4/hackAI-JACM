from app.agents.topic_extractor import TopicExtractorAgent
from app.agents.emotion_targeting import EmotionTargetingAgent
from app.agents.content_generator import ContentGeneratorAgent
from app.services.audience_service import AudienceExtractionService
from app.services.style_matching_service import StyleMatchingService
from app.database.context_operations import ContextPostsDB
from typing import Dict, List, Any, Optional, AsyncGenerator
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
logger = logging.getLogger(__name__)


class StreamingPipelineService:
    """
    Streaming service that processes content and yields posts as they're completed.
    
    Flow: Text → Audience → Topics → Enhanced Topics (with emotions + audience) → Content → Style Matching → Final Output (streamed as ready)
    """
    
    def __init__(self):
        # Initialize all five agents with configuration from environment
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-pro")
        temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.3"))
        
        self.audience_extractor = AudienceExtractionService()
        self.context_db = ContextPostsDB()
        self.style_matcher = StyleMatchingService()
        
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
        context_posts: Dict[str, List[str]] = {},
        target_platforms: Optional[List[str]] = None,
        original_url: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream social media posts as they're generated through the pipeline.
        
        Args:
            text: The original text to process
            context_posts: Context posts for style matching (maps platform to posts)
            target_platforms: List of target platforms (default: ["twitter"])
            original_url: URL of the original content (optional)
            
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
            
            # Step 1: Extract audience (0-15%)
            yield self._format_sse_event("status", {
                "message": "Analyzing target audience...",
                "stage": "audience_extraction",
                "progress": 5,
                "timestamp": datetime.now().isoformat()
            })
            
            audience_result = await self.audience_extractor.extract_audience(text)
            
            if not audience_result['success']:
                yield self._format_sse_event("error", {
                    "error": f"Audience extraction failed: {audience_result['error']}",
                    "stage": "audience_extraction"
                })
                return
            
            audience_context = audience_result.get('audience_summary', '')
            logger.info(f"✅ Step 1/5 - Audience extraction completed in {audience_result['processing_time']:.2f}s")
            logger.info(f"📝 Audience Summary: {audience_context[:200]}{'...' if len(audience_context) > 200 else ''}")
            
            yield self._format_sse_event("status", {
                "message": "Audience analysis complete",
                "stage": "audience_extraction_complete", 
                "progress": 15,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 2: Extract topics (15-30%)
            yield self._format_sse_event("status", {
                "message": "Extracting topics...",
                "stage": "topic_extraction",
                "progress": 20,
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
            logger.info(f"✅ Step 2/5 - Topic extraction completed in {topic_result['processing_time']:.2f}s, extracted {topic_result['total_topics']} topics")
            for i, topic in enumerate(topic_result['topics'], 1):
                logger.info(f"📝 Topic {i}: {topic['topic_name']}")
            
            yield self._format_sse_event("status", {
                "message": f"Found {topics_found} topics",
                "stage": "topic_extraction_complete",
                "topics_count": topics_found,
                "progress": 30,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 3: Analyze emotions for the extracted topics with audience context (30-45%)
            yield self._format_sse_event("status", {
                "message": "Analyzing emotions...",
                "stage": "emotion_analysis",
                "progress": 35,
                "timestamp": datetime.now().isoformat()
            })
            
            emotion_result = self.emotion_analyzer.analyze_emotions(
                topics=topic_result['topics'],
                audience_context=audience_context
            )
            
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
            
            logger.info(f"✅ Step 3/5 - Emotion analysis completed in {emotion_result['processing_time']:.2f}s, analyzed {len(emotion_result['emotion_analysis'])} topics")
            for i, enhanced_topic in enumerate(emotion_result['emotion_analysis'], 1):
                logger.info(f"📝 Topic {i} Emotion: {enhanced_topic['primary_emotion']} - {enhanced_topic['reasoning'][:100]}{'...' if len(enhanced_topic['reasoning']) > 100 else ''}")
            
            yield self._format_sse_event("status", {
                "message": f"Emotion analysis complete. Generating {total_posts_expected} posts...",
                "stage": "content_generation_start",
                "total_posts_expected": total_posts_expected,
                "platforms": target_platforms,
                "progress": 45,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 4: Generate content in parallel (45-75%) - DON'T stream posts yet
            generated_posts = []
            content_generation_time = 0
            
            async for event in self._stream_content_generation(
                enhanced_topics=enhanced_topics,
                original_text=text,
                original_url=original_url,
                audience_context=audience_context,
                target_platforms=target_platforms
            ):
                if event.startswith('event: generated_post\n'):
                    # Extract post data and store for style matching - DON'T yield to user yet
                    import json
                    data_line = event.split('\n')[1]  # Get the data line
                    post_data = json.loads(data_line[5:])  # Remove "data: " prefix
                    generated_posts.append(post_data)
                    content_generation_time += post_data['processing_time']
                else:
                    # Only yield status updates, not the actual posts
                    yield event
            
            logger.info(f"✅ Step 4/5 - Content generation completed in {content_generation_time:.2f}s, generated {len(generated_posts)} posts")
            for i, post in enumerate(generated_posts, 1):
                logger.info(f"📝 Generated Post {i}: {post['post_content'][:150]}{'...' if len(post['post_content']) > 150 else ''}")
            
            # Step 5: Apply style matching and stream FINAL posts (75-100%)
            yield self._format_sse_event("status", {
                "message": "Applying style matching...",
                "stage": "style_matching_start",
                "progress": 75,
                "timestamp": datetime.now().isoformat()
            })
            
            async for event in self._stream_style_matching(
                generated_posts=generated_posts,
                context_posts=context_posts
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
        audience_context: str,
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
                task = self._generate_content_only(
                    topic=topic,
                    original_text=original_text,
                    original_url=original_url,
                    audience_context=audience_context,
                    platform=platform
                )
                tasks.append(task)
                metadata = {
                    'topic_id': topic['topic_id'],
                    'topic_name': topic['topic_name'],
                    'platform': platform
                }
                task_metadata.append(metadata)
        
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
                # Calculate progress (45-75% for content generation only)
                content_progress = 45 + (posts_completed / len(tasks)) * 30
                
                # Stream progress status only - NOT the actual post content yet
                status_data = {
                    "message": f"Generated post {posts_completed}/{len(tasks)} for {metadata['platform']}",
                    "stage": "content_generation_progress",
                    "progress": round(content_progress),
                    "post_progress": {
                        "completed": posts_completed,
                        "total": len(tasks)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"🎉 Generated post: {metadata['platform']} - {result['post_content'][:50]}...")  # Debug log
                yield self._format_sse_event("status", status_data)
                
                # Store the post data for collection (will be styled later) - DON'T yield yet
                post_data = {
                    "post_content": result['post_content'],
                    "topic_id": metadata['topic_id'],
                    "topic_name": metadata['topic_name'],
                    "platform": metadata['platform'],
                    "primary_emotion": result.get('primary_emotion', ''),
                    "content_strategy": result['content_strategy'],
                    "processing_time": result['processing_time']
                }
                # This will be collected by the main stream_posts method for style matching
                yield self._format_sse_event("generated_post", post_data)
            else:
                # Calculate progress even for errors
                content_progress = 45 + (posts_completed / len(tasks)) * 30
                
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
    
    async def _generate_content_only(
        self,
        topic: Dict[str, Any],
        original_text: str,
        original_url: str,
        audience_context: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Generate content for a single topic/platform combination.
        Runs in thread pool to avoid blocking the event loop.
        """
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                content_result = await loop.run_in_executor(
                    executor,
                    self.content_generator.generate_content_for_topic,
                    topic,
                    original_text,
                    original_url,
                    platform,
                    audience_context
                )
            
            if not content_result['success']:
                content_result['primary_emotion'] = topic.get('primary_emotion', '')
                return content_result
            
            return {
                'success': True,
                'post_content': content_result['final_post'],
                'topic_id': topic['topic_id'],
                'topic_name': topic['topic_name'],
                'platform': platform,
                'primary_emotion': topic.get('primary_emotion', ''),
                'content_strategy': content_result['content_strategy'],
                'processing_time': content_result['processing_time']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Content generation failed: {str(e)}",
                'topic_id': topic['topic_id'],
                'topic_name': topic['topic_name'],
                'platform': platform,
                'primary_emotion': topic.get('primary_emotion', ''),
                'content_strategy': '',
                'processing_time': 0.0
            }
    
    async def _stream_style_matching(
        self,
        generated_posts: List[Dict[str, Any]],
        context_posts: Dict[str, List[str]]
    ) -> AsyncGenerator[str, None]:
        """
        Apply style matching to generated posts and stream final results.
        """
        posts_completed = 0
        total_posts = len(generated_posts)
        
        for i, post in enumerate(generated_posts):
            posts_completed += 1
            
            # Extract platform and context posts
            platform = post['platform']
            platform_context_posts = context_posts.get(platform, [])
            
            # Extract content before URL for style matching
            post_content = post['post_content']
            post_parts = post_content.rsplit(' ', 1)  # Split on last space
            if len(post_parts) == 2 and post_parts[1].startswith('http'):
                content_only = post_parts[0]
                url_part = post_parts[1]
            else:
                content_only = post_content
                url_part = ""
            
            final_post = post_content  # Default to original if style matching fails
            style_processing_time = 0.0
            
            # Apply style matching if context posts are available
            if platform_context_posts:
                logger.info(f"🔍 Applying style matching to post {i+1}: {post_content[:100]}{'...' if len(post_content) > 100 else ''}")
                try:
                    style_result = await self.style_matcher.match_style(
                        original_content=content_only,
                        context_posts=platform_context_posts,
                        platform=platform,
                        target_length=240  # Reserve space for URL
                    )
                    
                    if style_result['success']:
                        # Reconstruct final post with style-matched content + URL
                        if url_part:
                            final_post = f"{style_result['final_content']} {url_part}"
                        else:
                            final_post = style_result['final_content']
                        style_processing_time = style_result['processing_time']
                        logger.info(f"📝 Final Post {i+1}: {final_post[:150]}{'...' if len(final_post) > 150 else ''}")
                    else:
                        logger.warning(f"Style matching failed for post {i+1}: {style_result['error']}")
                
                except Exception as e:
                    logger.warning(f"Style matching error for post {i+1}: {str(e)}")
            
            # Calculate progress (75-100% for style matching)
            style_progress = 75 + (posts_completed / total_posts) * 25
            
            # Stream the final post
            final_post_data = {
                "post_content": final_post,
                "topic_id": post['topic_id'],
                "topic_name": post['topic_name'],
                "platform": post['platform'],
                "primary_emotion": post['primary_emotion'],
                "content_strategy": post['content_strategy'],
                "processing_time": post['processing_time'] + style_processing_time,
                "progress": round(style_progress),
                "post_progress": {
                    "completed": posts_completed,
                    "total": total_posts
                },
                "timestamp": datetime.now().isoformat()
            }
            
            yield self._format_sse_event("post", final_post_data)
    
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
    
    async def test_style_matching_only(
        self,
        mock_generated_posts: List[Dict[str, Any]] = None,
        mock_context_posts: Dict[str, List[str]] = None
    ) -> List[str]:
        """
        Test method to isolate and debug the _stream_style_matching function.
        
        Args:
            mock_generated_posts: Test posts to style match (optional)
            mock_context_posts: Test context posts (optional)
            
        Returns:
            List of SSE events as strings
        """
        # Use default test data if not provided
        if mock_generated_posts is None:
            mock_generated_posts = [
                {
                    'post_content': 'This is a test post about AI technology. https://example.com',
                    'topic_id': 'topic_1',
                    'topic_name': 'AI Technology',
                    'platform': 'twitter',
                    'primary_emotion': 'excitement',
                    'content_strategy': 'Educational with enthusiasm',
                    'processing_time': 1.5
                },
                {
                    'post_content': 'Another test post about machine learning innovations.',
                    'topic_id': 'topic_2', 
                    'topic_name': 'Machine Learning',
                    'platform': 'linkedin',
                    'primary_emotion': 'curiosity',
                    'content_strategy': 'Professional insight',
                    'processing_time': 2.0
                }
            ]
        
        if mock_context_posts is None:
            mock_context_posts = {
                'twitter': [
                    'Just discovered this amazing new AI tool! 🚀 Game changer for productivity.',
                    'Hot take: The future of work is human-AI collaboration, not replacement.',
                    'Mind blown by today\'s tech demo. Innovation never stops! 💡'
                ],
                'linkedin': [
                    'Reflecting on the transformative potential of artificial intelligence in enterprise solutions.',
                    'Excited to share insights from our latest research on machine learning applications.',
                    'The intersection of technology and human creativity continues to inspire new possibilities.'
                ]
            }
        
        print(f"🧪 Testing style matching with {len(mock_generated_posts)} posts")
        print(f"🧪 Context posts available for platforms: {list(mock_context_posts.keys())}")
        
        # Collect all SSE events
        events = []
        
        try:
            async for event in self._stream_style_matching(
                generated_posts=mock_generated_posts,
                context_posts=mock_context_posts
            ):
                events.append(event)
                print(f"📡 SSE Event: {event.strip()}")
        
        except Exception as e:
            error_event = self._format_sse_event("error", {
                "error": f"Style matching test failed: {str(e)}",
                "stage": "style_matching_test"
            })
            events.append(error_event)
            print(f"❌ Error during style matching test: {str(e)}")
        
        print(f"🧪 Test completed. Generated {len(events)} SSE events")
        return events
    
    async def get_user_context_posts(self, user_id: str, platform: str = None) -> List[Dict[str, Any]]:
        """Get user context posts from database by user_id"""
        try:
            return await self.context_db.get_user_context_posts(user_id, platform)
        except Exception as e:
            # Log error but don't fail the pipeline
            logger.error(f"Error getting context posts for user {user_id}: {str(e)}")
            return []
    
    async def get_context_posts_by_handle(self, x_handle: str, platform: str = None) -> List[Dict[str, Any]]:
        """Get context posts from database by x_handle"""
        try:
            return await self.context_db.get_context_posts_by_handle(x_handle, platform)
        except Exception as e:
            # Log error but don't fail the pipeline
            logger.error(f"Error getting context posts for handle {x_handle}: {str(e)}")
            return []


class StreamingPipelineError(Exception):
    """Custom exception for streaming pipeline errors"""
    pass 