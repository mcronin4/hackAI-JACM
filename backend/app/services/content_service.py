from app.agents.content_generator import ContentGeneratorAgent
from app.models import EnhancedTopic, GeneratedContent, ContentGenerationResponse
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

load_dotenv()


class ContentGenerationService:
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
    ) -> ContentGenerationResponse:
        """
        Generate content for multiple topics across specified platforms
        
        Args:
            original_text: The original long-form text
            topics: List of enhanced topics with emotion data
            original_url: URL of the original content
            target_platforms: List of target platforms (defaults to ["twitter"])
            
        Returns:
            ContentGenerationResponse with generated content for each topic/platform combination
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not original_text or not original_text.strip():
                raise ValueError("Original text cannot be empty")
            
            if not topics or len(topics) == 0:
                raise ValueError("At least one topic is required")
            
            if not original_url or not original_url.strip():
                raise ValueError("Original URL is required")
            
            if target_platforms is None:
                target_platforms = ["twitter"]
            
            # Generate content for each topic/platform combination
            generated_content = []
            
            # Process topics independently (as requested)
            for topic in topics:
                topic_dict = topic.dict() if hasattr(topic, 'dict') else topic
                
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
            
            return ContentGenerationResponse(
                generated_content=generated_content,
                total_generated=len(generated_content),
                successful_generations=successful_generations,
                total_processing_time=total_processing_time
            )
            
        except Exception as e:
            # Re-raise as a more specific exception
            raise ContentGenerationError(f"Failed to generate content: {str(e)}")
    
    async def generate_content_parallel(
        self, 
        original_text: str, 
        topics: List[EnhancedTopic], 
        original_url: str, 
        target_platforms: List[str] = None
    ) -> ContentGenerationResponse:
        """
        Generate content for multiple topics in parallel for better performance
        
        Args:
            original_text: The original long-form text
            topics: List of enhanced topics with emotion data
            original_url: URL of the original content
            target_platforms: List of target platforms (defaults to ["twitter"])
            
        Returns:
            ContentGenerationResponse with generated content for each topic/platform combination
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not original_text or not original_text.strip():
                raise ValueError("Original text cannot be empty")
            
            if not topics or len(topics) == 0:
                raise ValueError("At least one topic is required")
            
            if not original_url or not original_url.strip():
                raise ValueError("Original URL is required")
            
            if target_platforms is None:
                target_platforms = ["twitter"]
            
            # Create tasks for parallel execution
            tasks = []
            
            for topic in topics:
                topic_dict = topic.dict() if hasattr(topic, 'dict') else topic
                
                for platform in target_platforms:
                    task = self._generate_single_content(
                        topic_dict, original_text, original_url, platform
                    )
                    tasks.append(task)
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            generated_content = []
            for result in results:
                if isinstance(result, Exception):
                    # Handle exceptions
                    error_content = GeneratedContent(
                        topic_id=0,  # Will be set properly in real implementation
                        platform="unknown",
                        final_post="",
                        content_strategy="",
                        hashtags=[],
                        call_to_action="",
                        success=False,
                        error=f"Parallel execution error: {str(result)}",
                        processing_time=0.0
                    )
                    generated_content.append(error_content)
                else:
                    generated_content.append(result)
            
            # Calculate totals
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            successful_generations = len([c for c in generated_content if c.success])
            
            return ContentGenerationResponse(
                generated_content=generated_content,
                total_generated=len(generated_content),
                successful_generations=successful_generations,
                total_processing_time=total_processing_time
            )
            
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate content in parallel: {str(e)}")
    
    async def _generate_single_content(
        self, 
        topic: Dict[str, Any], 
        original_text: str, 
        original_url: str, 
        platform: str
    ) -> GeneratedContent:
        """
        Generate content for a single topic/platform combination
        Used for parallel execution
        """
        try:
            # Run the synchronous agent method in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    self.agent.generate_content_for_topic,
                    topic,
                    original_text,
                    original_url,
                    platform
                )
            
            return GeneratedContent(
                topic_id=topic['topic_id'],
                platform=platform,
                final_post=result['final_post'],
                content_strategy=result['content_strategy'],
                hashtags=[],  # No hashtags in integrated approach
                call_to_action=result['call_to_action'],
                success=result['success'],
                error=result.get('error'),
                processing_time=result['processing_time']
            )
            
        except Exception as e:
            return GeneratedContent(
                topic_id=topic.get('topic_id', 0),
                platform=platform,
                final_post="",
                content_strategy="",
                hashtags=[],
                call_to_action="",
                success=False,
                error=f"Failed to generate content: {str(e)}",
                processing_time=0.0
            )
    
    def get_agent_status(self) -> dict:
        """Get the status of the content generation agent"""
        return {
            "status": "ready",
            "model": self.agent.llm.model,
            "temperature": self.agent.llm.temperature,
            "supported_platforms": self.agent.platform_config.get_supported_platforms()
        }
    
    def get_platform_config(self, platform: str) -> dict:
        """Get configuration for a specific platform"""
        try:
            config = self.agent.platform_config.get_config(platform)
            return config.dict()
        except ValueError as e:
            raise ContentGenerationError(str(e))


class ContentGenerationError(Exception):
    """Custom exception for content generation errors"""
    pass 