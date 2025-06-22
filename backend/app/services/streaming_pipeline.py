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
            
            # Step 3-4: Process each topic in parallel through emotion analysis → content generation (30-75%)
            yield self._format_sse_event("status", {
                "message": f"Processing {len(topic_result['topics'])} topics in parallel (emotion analysis → content generation)...",
                "stage": "parallel_processing_start",
                "progress": 35,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process each topic through its complete pipeline in parallel
            generated_posts = []
            content_generation_time = 0
            
            async for event in self._stream_parallel_topic_processing(
                topics=topic_result['topics'],
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
                    content_generation_time += post_data.get('processing_time', 0)
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
    
    async def _stream_parallel_topic_processing(
        self,
        topics: List[Dict[str, Any]],
        original_text: str,
        original_url: str,
        audience_context: str,
        target_platforms: List[str]
    ) -> AsyncGenerator[str, None]:
        """
        Process each topic through the complete pipeline in parallel:
        Each topic goes through emotion analysis → content generation sequentially,
        but all topics run their pipelines in parallel with each other.
        """
        # Create tasks for parallel topic processing
        tasks = []
        task_metadata = []
        
        for topic in topics:
            task = self._process_single_topic_pipeline(
                topic=topic,
                original_text=original_text,
                original_url=original_url,
                audience_context=audience_context,
                target_platforms=target_platforms
            )
            tasks.append(task)
            task_metadata.append({
                'topic_id': topic['topic_id'],
                'topic_name': topic['topic_name']
            })
        
        # Execute all topic pipelines in parallel
        total_posts_expected = len(topics) * len(target_platforms)
        posts_completed = 0
        
        # Use asyncio.as_completed to yield results as they come in
        for task_coro in asyncio.as_completed(tasks):
            try:
                topic_result = await task_coro
                
                if topic_result['success']:
                    # Stream all posts for this topic
                    for post_result in topic_result['posts']:
                        posts_completed += 1
                        progress = 30 + (posts_completed / total_posts_expected) * 45  # 30-75%
                        
                        # Stream progress status
                        yield self._format_sse_event("status", {
                            "message": f"Generated post {posts_completed}/{total_posts_expected}",
                            "stage": "parallel_processing_progress",
                            "progress": round(progress),
                            "post_progress": {
                                "completed": posts_completed,
                                "total": total_posts_expected
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Stream the post data for collection
                        yield self._format_sse_event("generated_post", post_result)
                        
                else:
                    # Handle topic processing errors
                    yield self._format_sse_event("post_error", {
                        "error": f"Topic processing failed: {topic_result['error']}",
                        "topic_id": topic_result.get('topic_id', 'unknown'),
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                yield self._format_sse_event("post_error", {
                    "error": f"Topic processing exception: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })

    async def _process_single_topic_pipeline(
        self,
        topic: Dict[str, Any],
        original_text: str,
        original_url: str,
        audience_context: str,
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Process a single topic through: emotion analysis → content generation
        """
        try:
            # Step 1: Emotion analysis for this topic
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                emotion_result = await loop.run_in_executor(
                    executor,
                    self.emotion_analyzer.analyze_emotions,
                    [topic],  # Pass as list since method expects list
                    audience_context
                )
            
            if not emotion_result['success'] or not emotion_result['emotion_analysis']:
                return {
                    'success': False,
                    'topic_id': topic['topic_id'],
                    'error': f"Emotion analysis failed: {emotion_result.get('error', 'No results')}"
                }
            
            enhanced_topic = emotion_result['emotion_analysis'][0]  # Get first result
            logger.info(f"📝 Topic {topic['topic_id']} Emotion: {enhanced_topic['primary_emotion']}")
            
            # Step 2: Content generation for all platforms
            content_results = []
            
            for platform in target_platforms:
                try:
                    content_result = await self._generate_content_only(
                        topic=enhanced_topic,
                        original_text=original_text,
                        original_url=original_url,
                        audience_context=audience_context,
                        platform=platform
                    )
                    
                    if content_result['success']:
                        content_results.append({
                            "post_content": content_result['post_content'],
                            "topic_id": enhanced_topic['topic_id'],
                            "topic_name": enhanced_topic['topic_name'],
                            "platform": platform,
                            "primary_emotion": enhanced_topic.get('primary_emotion', ''),
                            "content_strategy": content_result['content_strategy'],
                            "processing_time": content_result['processing_time']
                        })
                    else:
                        return {
                            'success': False,
                            'topic_id': topic['topic_id'],
                            'error': f"Content generation failed for {platform}: {content_result.get('error', 'Unknown error')}"
                        }
                        
                except Exception as e:
                    return {
                        'success': False,
                        'topic_id': topic['topic_id'],
                        'error': f"Content generation exception for {platform}: {str(e)}"
                    }
            
            return {
                'success': True,
                'topic_id': topic['topic_id'],
                'posts': content_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'topic_id': topic.get('topic_id', 'unknown'),
                'error': f"Topic pipeline exception: {str(e)}"
            }

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