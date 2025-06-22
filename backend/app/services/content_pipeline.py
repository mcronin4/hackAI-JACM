from app.agents.topic_extractor import TopicExtractorAgent
from app.agents.emotion_targeting import EmotionTargetingAgent
from app.agents.content_generator import ContentGeneratorAgent
from app.services.audience_service import AudienceExtractionService
from app.services.style_matching_service import StyleMatchingService
from app.database.context_operations import ContextPostsDB
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

logger = logging.getLogger(__name__)


class ContentPipelineService:
    """
    Unified service that chains together audience extraction, topic extraction, emotion analysis, content generation, and style matching.
    
    Flow: Text → Audience → Topics → [Per Topic in Parallel: Enhanced Topics (with emotions + audience) → Content → Style Matching] → Final Output
    """
    
    def __init__(self):
        # Initialize all five agents with configuration from environment
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
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
    
    async def process_content(
        self,
        text: str,
        context_posts: Dict[str, List[str]], # This maps platform to a list of posts gotten from the database and used for style matching
        target_platforms: Optional[List[str]] = None,
        original_url: Optional[str] = None

    ) -> Dict[str, Any]:
        """
        Process text through the complete pipeline with full parallelization: 
        extract audience → extract topics → [parallel per topic: analyze emotions → generate content → style matching]
        
        Args:
            text: The original text to process
            original_url: URL of the original content (optional)
            context_posts: Context posts for style matching (final stage)
            target_platforms: List of target platforms (default: ["twitter"])
            
        Returns:
            Dict with success status, generated posts, and metadata
        """
        start_time = datetime.now()
        
        try:
            # Input validation
            if not text or not text.strip():
                return self._create_error_response("Text cannot be empty", start_time)
            
            # Use empty string as default if no URL provided
            if not original_url:
                original_url = ""
            
            if target_platforms is None:
                target_platforms = ["twitter"]
            
            # Step 1: Extract audience
            audience_result = await self.audience_extractor.extract_audience(text)
            
            if not audience_result['success']:
                return self._create_error_response(
                    f"Audience extraction failed: {audience_result['error']}", 
                    start_time
                )
            
            audience_context = audience_result.get('audience_summary', '')
            logger.info(f"✅ Step 1/5 - Audience extraction completed in {audience_result['processing_time']:.2f}s")
            logger.info(f"📝 Audience Summary: {audience_context[:200]}{'...' if len(audience_context) > 200 else ''}")
            
            # Step 2: Extract topics
            topic_result = self.topic_extractor.extract_topics(text)
            
            if not topic_result['success']:
                return self._create_error_response(
                    f"Topic extraction failed: {topic_result['error']}", 
                    start_time
                )
            
            if not topic_result['topics']:
                return self._create_error_response(
                    "No topics were extracted from the text", 
                    start_time
                )
            
            logger.info(f"✅ Step 2/5 - Topic extraction completed in {topic_result['processing_time']:.2f}s, extracted {topic_result['total_topics']} topics")
            for i, topic in enumerate(topic_result['topics'], 1):
                logger.info(f"📝 Topic {i}: {topic['topic_name']}")
            
            # Step 3-5: Process each topic in parallel through the remaining pipeline
            # Each topic goes through: emotion analysis → content generation → style matching sequentially
            # But all topics can run this workflow in parallel with each other
            tasks = []
            for topic in topic_result['topics']:
                task = self._process_topic_pipeline(
                    topic=topic,
                    text=text,
                    audience_context=audience_context,
                    original_url=original_url,
                    target_platforms=target_platforms,
                    context_posts=context_posts
                )
                tasks.append(task)
            
            # Execute all topic pipelines in parallel
            logger.info(f"🚀 Step 3-5/5 - Processing {len(tasks)} topics in parallel (each topic: emotion analysis → content generation → style matching)")
            topic_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and organize by platform
            platform_posts = {}
            for platform in target_platforms:
                platform_posts[platform] = []
            
            successful_generations = 0
            failed_generations = []
            total_emotion_time = 0
            total_content_time = 0
            total_style_time = 0
            
            for result in topic_results:
                if isinstance(result, Exception):
                    failed_generations.append(f"Topic pipeline error: {str(result)}")
                    continue
                
                if result['success']:
                    # Add timing information
                    total_emotion_time += result['emotion_time']
                    total_content_time += result['content_time']
                    total_style_time += result['style_time']
                    
                    # Organize posts by platform
                    for platform_data in result['platform_results']:
                        if platform_data['success']:
                            platform_posts[platform_data['platform']].append({
                                'post_content': platform_data['final_post'],
                                'topic_id': result['topic']['topic_id'],
                                'topic_name': result['topic']['topic_name'],
                                'primary_emotion': result['emotion_analysis']['primary_emotion'],
                                'content_strategy': platform_data['content_strategy'],
                                'processing_time': platform_data['processing_time'],
                                'style_matched': platform_data.get('style_matched', False)
                            })
                            successful_generations += 1
                        else:
                            failed_generations.append(
                                f"Topic {result['topic']['topic_id']}/{platform_data['platform']}: {platform_data['error']}"
                            )
                else:
                    failed_generations.append(f"Topic {result.get('topic', {}).get('topic_id', 'unknown')}: {result['error']}")
            
            # Check if any content generation failed
            if failed_generations:
                error_details = "; ".join(failed_generations)
                return self._create_error_response(
                    f"Some topic processing failed: {error_details}",
                    start_time
                )
            
            total_processing_time = total_emotion_time + total_content_time + total_style_time
            
            logger.info(f"✅ Step 3-5/5 - Parallel processing completed in max({total_emotion_time:.2f}s emotion, {total_content_time:.2f}s content, {total_style_time:.2f}s style)")
            logger.info(f"📊 Generated {successful_generations} posts total")
            for platform, posts in platform_posts.items():
                for i, post in enumerate(posts, 1):
                    logger.info(f"📝 Generated Post {i} on {platform}: {post['post_content'][:150]}{'...' if len(post['post_content']) > 150 else ''}")
            
            # Calculate total pipeline time
            end_time = datetime.now()
            total_pipeline_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'platform_posts': platform_posts,
                'metadata': {
                    'total_topics': len(topic_result['topics']),
                    'successful_generations': successful_generations,
                    'failed_generations': len(failed_generations),
                    'audience_extraction_time': audience_result['processing_time'],
                    'topic_extraction_time': topic_result['processing_time'],
                    'parallel_processing_time': total_processing_time,
                    'total_pipeline_time': total_pipeline_time,
                    'audience_summary': audience_context[:200] + '...' if len(audience_context) > 200 else audience_context,
                    'original_url': original_url,
                    'target_platforms': target_platforms
                },
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return self._create_error_response(f"Pipeline execution failed: {str(e)}", start_time)

    async def _process_topic_pipeline(
        self,
        topic: Dict[str, Any],
        text: str,
        audience_context: str,
        original_url: str,
        target_platforms: List[str],
        context_posts: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Process a single topic through the complete pipeline sequentially:
        emotion analysis → content generation → style matching
        
        This entire pipeline runs independently for each topic in parallel.
        
        Args:
            topic: Topic dictionary from topic extraction
            text: Original text
            audience_context: Audience summary
            original_url: Original URL
            target_platforms: List of platforms to generate for
            context_posts: Context posts for style matching
            
        Returns:
            Dict with processing results for this topic
        """
        try:
            start_time = datetime.now()
            
            # Step 3: Emotion analysis for this topic
            emotion_start = datetime.now()
            emotion_result = await self._run_emotion_analysis(topic, audience_context)
            emotion_time = (datetime.now() - emotion_start).total_seconds()
            
            if not emotion_result['success']:
                return {
                    'success': False,
                    'topic': topic,
                    'error': f"Emotion analysis failed: {emotion_result['error']}",
                    'emotion_time': emotion_time,
                    'content_time': 0,
                    'style_time': 0
                }
            
            enhanced_topic = emotion_result['emotion_analysis']
            logger.info(f"📝 Topic {topic['topic_id']} Emotion: {enhanced_topic['primary_emotion']} - {enhanced_topic['reasoning'][:100]}{'...' if len(enhanced_topic['reasoning']) > 100 else ''}")
            
            # Step 4-5: Process each platform sequentially (since content gen → style matching are dependent)
            # But we can still parallelize across platforms for this topic
            platform_tasks = []
            
            for platform in target_platforms:
                task = self._process_platform_content(
                    enhanced_topic=enhanced_topic,
                    text=text,
                    original_url=original_url,
                    audience_context=audience_context,
                    platform=platform,
                    context_posts=context_posts.get(platform, [])
                )
                platform_tasks.append(task)
            
            # Execute all platforms for this topic in parallel
            platform_results = await asyncio.gather(*platform_tasks, return_exceptions=True)
            content_time = (datetime.now() - emotion_start).total_seconds() - emotion_time
            
            # Process platform results
            processed_results = []
            max_style_time = 0
            
            for i, result in enumerate(platform_results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'success': False,
                        'platform': target_platforms[i],
                        'error': str(result),
                        'processing_time': 0
                    })
                else:
                    processed_results.append(result)
                    max_style_time = max(max_style_time, result.get('style_time', 0))
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'topic': topic,
                'emotion_analysis': enhanced_topic,
                'platform_results': processed_results,
                'emotion_time': emotion_time,
                'content_time': content_time,
                'style_time': max_style_time,
                'total_topic_time': total_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'topic': topic,
                'error': str(e),
                'emotion_time': 0,
                'content_time': 0,
                'style_time': 0
            }

    async def _run_emotion_analysis(self, topic: Dict[str, Any], audience_context: str) -> Dict[str, Any]:
        """Run emotion analysis for a single topic in thread pool"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                emotion_result = await loop.run_in_executor(
                    executor,
                    self.emotion_analyzer.analyze_emotions,
                    [topic],  # Pass as list since the method expects a list
                    audience_context
                )
            
            if emotion_result['success'] and emotion_result['emotion_analysis']:
                return {
                    'success': True,
                    'emotion_analysis': emotion_result['emotion_analysis'][0]  # Get first (and only) result
                }
            else:
                return {
                    'success': False,
                    'error': emotion_result.get('error', 'Unknown emotion analysis error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Emotion analysis execution error: {str(e)}"
            }

    async def _process_platform_content(
        self,
        enhanced_topic: Dict[str, Any],
        text: str,
        original_url: str,
        audience_context: str,
        platform: str,
        context_posts: List[str]
    ) -> Dict[str, Any]:
        """
        Process content generation and style matching for a single platform
        """
        try:
            # Step 4: Content generation
            content_result = await self._run_content_generation(
                enhanced_topic, text, original_url, platform, audience_context
            )
            
            if not content_result['success']:
                return {
                    'success': False,
                    'platform': platform,
                    'error': f"Content generation failed: {content_result['error']}",
                    'processing_time': content_result.get('processing_time', 0),
                    'style_time': 0
                }
            
            generated_content = content_result['final_post']
            content_processing_time = content_result['processing_time']
            
            # Step 5: Style matching
            style_start = datetime.now()
            style_result = await self._run_style_matching(
                generated_content, context_posts, platform
            )
            style_time = (datetime.now() - style_start).total_seconds()
            
            final_content = generated_content  # Default to original content
            style_matched = False
            
            if style_result['success'] and not style_result.get('skipped', False):
                final_content = style_result['final_content']
                style_matched = True
                logger.info(f"✅ Style matching applied for {platform} on topic {enhanced_topic['topic_id']}")
            elif style_result.get('skipped', False):
                logger.info(f"⏭️ Style matching skipped for {platform} on topic {enhanced_topic['topic_id']} (no context posts)")
            else:
                logger.warning(f"⚠️ Style matching failed for {platform} on topic {enhanced_topic['topic_id']}: {style_result.get('error', 'Unknown error')}")
            
            return {
                'success': True,
                'platform': platform,
                'final_post': final_content,
                'content_strategy': content_result['content_strategy'],
                'processing_time': content_processing_time + style_time,
                'style_time': style_time,
                'style_matched': style_matched
            }
            
        except Exception as e:
            return {
                'success': False,
                'platform': platform,
                'error': str(e),
                'processing_time': 0,
                'style_time': 0
            }

    async def _run_content_generation(
        self,
        enhanced_topic: Dict[str, Any],
        text: str,
        original_url: str,
        platform: str,
        audience_context: str
    ) -> Dict[str, Any]:
        """Run content generation for a single topic/platform in thread pool"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                content_result = await loop.run_in_executor(
                    executor,
                    self.content_generator.generate_content_for_topic,
                    enhanced_topic,
                    text,
                    original_url,
                    platform,
                    audience_context
                )
            
            return content_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Content generation execution error: {str(e)}",
                'processing_time': 0
            }

    async def _run_style_matching(
        self,
        content: str,
        context_posts: List[str],
        platform: str
    ) -> Dict[str, Any]:
        """Run style matching for content in thread pool"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                style_result = await loop.run_in_executor(
                    executor,
                    self.style_matcher.match_style,
                    content,
                    context_posts,
                    platform,
                    240  # Default target length
                )
            
            return style_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Style matching execution error: {str(e)}",
                'skipped': False
            }

    def _create_error_response(self, error_message: str, start_time: datetime) -> Dict[str, Any]:
        """Create standardized error response"""
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            'success': False,
            'error': error_message,
            'platform_posts': {},  # NEW: Empty platform posts structure
            'generated_posts': [],  # LEGACY: Empty list for backwards compatibility
            'total_topics': 0,
            'successful_generations': 0,
            'processing_time': processing_time
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the status of all agents in the pipeline"""
        return {
            'status': 'ready',
            'agents': {
                'audience_extractor': self.audience_extractor.get_agent_status(),
                'topic_extractor': {
                    'model': self.topic_extractor.llm.model,
                    'temperature': self.topic_extractor.llm.temperature
                },
                'emotion_analyzer': {
                    'model': self.emotion_analyzer.llm.model,
                    'temperature': self.emotion_analyzer.llm.temperature
                },
                'content_generator': {
                    'model': self.content_generator.llm.model,
                    'temperature': self.content_generator.llm.temperature,
                    'supported_platforms': self.content_generator.platform_config.get_supported_platforms()
                },
                'style_matcher': self.style_matcher.get_agent_status()
            }
        }
    
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


class ContentPipelineError(Exception):
    """Custom exception for content pipeline errors"""
    pass 