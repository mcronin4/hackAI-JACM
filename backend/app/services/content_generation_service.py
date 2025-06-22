from app.agents.content_generator import ContentGeneratorAgent
from app.models import EnhancedTopic, GeneratedContent, ContentGenerationOnlyResponse
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class ContentGenerationOnlyService:
    def __init__(self):
        # Initialize the agent with configuration from environment
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
        temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.3"))
        
        self.agent = ContentGeneratorAgent(
            model_name=model_name,
            temperature=temperature
        )
    
    async def generate_content(
        self, 
        original_text: str,
        topics: List[EnhancedTopic], 
        original_url: str,
        target_platforms: List[str] = None
    ) -> ContentGenerationOnlyResponse:
        """
        Generate content for enhanced topics using the content generation agent
        
        Args:
            original_text: The original long-form text
            topics: List of enhanced topics with emotion data
            original_url: URL of the original content
            target_platforms: List of target platforms (defaults to ["twitter"])
            
        Returns:
            ContentGenerationOnlyResponse with generated content
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not original_text or not original_text.strip():
                raise ValueError("Original text cannot be empty")
            
            if not topics or len(topics) == 0:
                raise ValueError("Topics list cannot be empty")
            
            if not original_url or not original_url.strip():
                raise ValueError("Original URL is required")
            
            if target_platforms is None:
                target_platforms = ["twitter"]
            
            # Generate content for each topic/platform combination
            generated_content = []
            
            for topic in topics:
                # Convert EnhancedTopic to dictionary for the agent
                topic_dict = {
                    'topic_id': topic.topic_id,
                    'topic_name': topic.topic_name,
                    'content_excerpt': topic.content_excerpt,
                    'primary_emotion': topic.primary_emotion,
                    'emotion_description': topic.emotion_description,
                    'emotion_confidence': topic.emotion_confidence,
                    'reasoning': topic.reasoning
                }
                
                for platform in target_platforms:
                    try:
                        result = self.agent.generate_content_for_topic(
                            topic=topic_dict,
                            original_text=original_text,
                            original_url=original_url,
                            platform=platform
                        )
                        
                        content = GeneratedContent(
                            topic_id=topic_dict['topic_id'],
                            platform=platform,
                            final_post=result['final_post'],
                            content_strategy=result['content_strategy'],
                            hashtags=[],  # No hashtags in integrated approach
                            call_to_action=result['call_to_action'],
                            success=result['success'],
                            error=result.get('error'),
                            processing_time=result['processing_time']
                        )
                        
                        generated_content.append(content)
                        
                    except Exception as e:
                        # Continue with other topics even if one fails
                        error_content = GeneratedContent(
                            topic_id=topic_dict['topic_id'],
                            platform=platform,
                            final_post="",
                            content_strategy="",
                            hashtags=[],
                            call_to_action="",
                            success=False,
                            error=f"Failed to generate content: {str(e)}",
                            processing_time=0.0
                        )
                        generated_content.append(error_content)
            
            # Calculate totals
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            successful_generations = len([c for c in generated_content if c.success])
            
            return ContentGenerationOnlyResponse(
                success=successful_generations > 0,
                generated_content=generated_content,
                total_generated=len(generated_content),
                successful_generations=successful_generations,
                processing_time=total_processing_time,
                error=None if successful_generations > 0 else "No content was successfully generated"
            )
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return ContentGenerationOnlyResponse(
                success=False,
                generated_content=[],
                total_generated=0,
                successful_generations=0,
                processing_time=processing_time,
                error=f"Failed to generate content: {str(e)}"
            )
    
    def get_agent_status(self) -> dict:
        """Get the status of the content generation agent"""
        return {
            "status": "ready",
            "model": self.agent.llm.model,
            "temperature": self.agent.llm.temperature,
            "supported_platforms": self.agent.platform_config.get_supported_platforms(),
            "agent_type": "content_generator"
        }
    
    def get_platform_config(self, platform: str) -> dict:
        """Get configuration for a specific platform"""
        try:
            config = self.agent.platform_config.get_config(platform)
            return config.dict()
        except ValueError as e:
            raise ContentGenerationOnlyError(str(e))


class ContentGenerationOnlyError(Exception):
    """Custom exception for content generation errors"""
    pass 