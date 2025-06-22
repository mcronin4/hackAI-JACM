from app.agents.topic_extractor import TopicExtractorAgent
from app.agents.emotion_targeting import EmotionTargetingAgent
from app.agents.content_generator import ContentGeneratorAgent
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio

load_dotenv()


class ContentPipelineService:
    """
    Unified service that chains together topic extraction, emotion analysis, and content generation.
    
    Flow: Text → Topics → Enhanced Topics (with emotions) → Content
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
    
    async def process_content(
        self,
        text: str,
        original_url: str,
        target_platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process text through the complete pipeline: extract topics → analyze emotions → generate content
        
        Args:
            text: The original text to process
            original_url: URL of the original content
            target_platforms: List of target platforms (default: ["twitter"])
            
        Returns:
            Dict with success status, generated posts, and metadata
        """
        start_time = datetime.now()
        
        try:
            # Input validation
            if not text or not text.strip():
                return self._create_error_response("Text cannot be empty", start_time)
            
            if not original_url or not original_url.strip():
                return self._create_error_response("Original URL cannot be empty", start_time)
            
            if target_platforms is None:
                target_platforms = ["twitter"]
            
            # Step 1: Extract topics
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
            
            # Step 2: Analyze emotions for the extracted topics
            emotion_result = self.emotion_analyzer.analyze_emotions(topic_result['topics'])
            
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
            
            # Step 3: Generate content for each enhanced topic and platform
            generated_posts = []
            successful_generations = 0
            failed_generations = []
            
            for enhanced_topic in emotion_result['emotion_analysis']:
                for platform in target_platforms:
                    try:
                        content_result = self.content_generator.generate_content_for_topic(
                            topic=enhanced_topic,
                            original_text=text,
                            original_url=original_url,
                            platform=platform
                        )
                        
                        if content_result['success']:
                            generated_posts.append(content_result['final_post'])
                            successful_generations += 1
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
            
            # Calculate final processing time
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'generated_posts': generated_posts,
                'total_topics': topic_result['total_topics'],
                'successful_generations': successful_generations,
                'processing_time': total_processing_time,
                'pipeline_details': {
                    'topic_extraction_time': topic_result['processing_time'],
                    'emotion_analysis_time': emotion_result['processing_time'],
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
            'generated_posts': [],
            'total_topics': 0,
            'successful_generations': 0,
            'processing_time': processing_time
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the status of all agents in the pipeline"""
        return {
            'status': 'ready',
            'agents': {
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
                }
            }
        }


class ContentPipelineError(Exception):
    """Custom exception for content pipeline errors"""
    pass 