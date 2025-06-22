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

load_dotenv()

logger = logging.getLogger(__name__)


class ContentPipelineService:
    """
    Unified service that chains together audience extraction, topic extraction, emotion analysis, content generation, and style matching.
    
    Flow: Text → Audience → Topics → Enhanced Topics (with emotions + audience) → Content → Style Matching → Final Output
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
        Process text through the complete pipeline: extract audience → extract topics → analyze emotions → generate content → style matching
        
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
            
            # Step 3: Analyze emotions for the extracted topics with audience context
            emotion_result = self.emotion_analyzer.analyze_emotions(
                topics=topic_result['topics'],
                audience_context=audience_context
            )
            
            if not emotion_result['success']:
                return self._create_error_response(
                    f"Emotion analysis failed: {emotion_result['error']}", 
                    start_time
                )
            
            if not emotion_result['emotion_analysis']:
                return self._create_error_response(
                    "No emotion analysis results were generated", 
                    start_time
                )
            
            logger.info(f"✅ Step 3/5 - Emotion analysis completed in {emotion_result['processing_time']:.2f}s, analyzed {len(emotion_result['emotion_analysis'])} topics")
            for i, enhanced_topic in enumerate(emotion_result['emotion_analysis'], 1):
                logger.info(f"📝 Topic {i} Emotion: {enhanced_topic['primary_emotion']} - {enhanced_topic['reasoning'][:100]}{'...' if len(enhanced_topic['reasoning']) > 100 else ''}")
            
            # Step 4: Generate content for each enhanced topic and platform
            platform_posts = {}  # Organize posts by platform
            successful_generations = 0
            failed_generations = []
            content_generation_time = 0

            
            # Initialize platform_posts structure
            for platform in target_platforms:
                platform_posts[platform] = []
            
            # Initialize platform_posts structure
            for platform in target_platforms:
                platform_posts[platform] = []
            
            for enhanced_topic in emotion_result['emotion_analysis']:
                for platform in target_platforms:
                    try:
                        content_result = self.content_generator.generate_content_for_topic(
                            topic=enhanced_topic,
                            original_text=text,
                            original_url=original_url,
                            platform=platform,
                            audience_context=audience_context
                        )
                        
                        if content_result['success']:
                            # Store post with metadata for each platform
                            post_data = {
                                'post_content': content_result['final_post'],
                                'topic_id': enhanced_topic['topic_id'],
                                'topic_name': enhanced_topic['topic_name'],
                                'primary_emotion': enhanced_topic['primary_emotion'],
                                'content_strategy': content_result['content_strategy'],
                                'processing_time': content_result['processing_time']
                            }
                            platform_posts[platform].append(post_data)
                            successful_generations += 1
                            content_generation_time += content_result['processing_time']
                        else:
                            failed_generations.append(
                                f"Topic {enhanced_topic['topic_id']}/{platform}: {content_result['error']}"
                            )
                    
                    except Exception as e:
                        failed_generations.append(
                            f"Topic {enhanced_topic['topic_id']}/{platform}: {str(e)}"
                        )
            
            # Check if any content generation failed (fail entire flow as per requirements)
            if failed_generations:
                error_details = "; ".join(failed_generations)
                return self._create_error_response(
                    f"Content generation failed for some topics: {error_details}",
                    start_time
                )
            
            logger.info(f"✅ Step 4/5 - Content generation completed in {content_generation_time:.2f}s, generated {successful_generations} posts")
            for platform, posts in platform_posts.items():
                for i, post in enumerate(posts, 1):
                    logger.info(f"📝 Generated Post {i} on {platform}: {post['post_content'][:150]}{'...' if len(post['post_content']) > 150 else ''}")
            
            # Step 5: Apply style matching to each generated post
            final_posts = {}  # Organize posts by platform
            style_matching_time = 0
            style_matching_failures = []

            # Initialize final_posts structure
            for platform in target_platforms:
                final_posts[platform] = []

            for platform, posts in platform_posts.items():      
                for i, post in enumerate(posts):
                    # Extract content before URL for style matching
                    post_parts = post.rsplit(' ', 1)  # Split on last space
                    if len(post_parts) == 2 and post_parts[1].startswith('http'):
                        content_only = post_parts[0]
                        url_part = post_parts[1]
                    else:
                        content_only = post
                        url_part = ""
                    
                    # Apply style matching for each platform
                    platform = target_platforms[i % len(target_platforms)]
                    platform_context_posts = context_posts.get(platform, [])
                    
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
                            final_posts[platform].append(final_post)
                            style_matching_time += style_result['processing_time']
                        else:
                            # If style matching fails, fall back to original
                            final_posts[platform].append(post)
                            style_matching_failures.append(f"Post {i+1}: {style_result['error']}")
                    
                    except Exception as e:
                        # If style matching fails, fall back to original
                        final_posts.append(post)
                        style_matching_failures.append(f"Post {i+1}: {str(e)}")

            # Log style matching results
            posts_processed = len(final_posts)
            posts_with_failures = len(style_matching_failures)
            posts_successfully_matched = posts_processed - posts_with_failures
            logger.info(f"✅ Step 5/5 - Style matching completed in {style_matching_time:.2f}s, {posts_successfully_matched}/{posts_processed} posts processed successfully")
            for i, final_post in enumerate(final_posts, 1):
                logger.info(f"📝 Final Post {i}: {final_post[:150]}{'...' if len(final_post) > 150 else ''}")
            
            # Calculate final processing time
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'generated_posts': final_posts,
                'total_topics': topic_result['total_topics'],
                'successful_generations': successful_generations,
                'processing_time': total_processing_time,
                'pipeline_details': {
                    'audience_extraction_time': audience_result['processing_time'],
                    'topic_extraction_time': topic_result['processing_time'],
                    'emotion_analysis_time': emotion_result['processing_time'],
                    'content_generation_time': content_generation_time,
                    'style_matching_time': style_matching_time,
                    'style_matching_failures': style_matching_failures,
                    'platforms_processed': target_platforms
                }
            }
            
        except Exception as e:
            return self._create_error_response(
                f"Pipeline processing error: {str(e)}", 
                start_time
            )
    
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
        """Get user context posts from database"""
        try:
            return await self.context_db.get_user_context_posts(user_id, platform)
        except Exception as e:
            # Log error but don't fail the pipeline
            return []


class ContentPipelineError(Exception):
    """Custom exception for content pipeline errors"""
    pass 