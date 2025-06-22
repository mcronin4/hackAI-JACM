from typing import Dict, List, Any
from app.agents.style_matching import StyleMatchingAgent
import logging

logger = logging.getLogger(__name__)


class StyleMatchingError(Exception):
    """Custom exception for style matching errors"""
    pass


class StyleMatchingService:
    def __init__(self):
        self.agent = StyleMatchingAgent()
    
    async def match_style(
        self,
        original_content: str,
        context_posts: List[str],
        platform: str = "twitter",
        target_length: int = 240
    ) -> Dict[str, Any]:
        """
        Match content style to user's previous posts
        
        Args:
            original_content: The generated content to style-match
            context_posts: List of user's previous posts for style reference
            platform: Target platform (affects length limits)
            target_length: Maximum character length for the content
            
        Returns:
            Dict containing success status, final content, and metadata
        """
        try:
            logger.info(f"Starting style matching for {len(original_content)} char content with {len(context_posts)} context posts")
            
            result = self.agent.match_style(
                original_content=original_content,
                context_posts=context_posts,
                platform=platform,
                target_length=target_length
            )
            
            if not result['success']:
                logger.error(f"Style matching failed: {result['error']}")
                raise StyleMatchingError(result['error'])
            
            logger.info(f"Style matching completed in {result['processing_time']:.2f}s, skipped: {result['skipped']}")
            
            return result
            
        except StyleMatchingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in style matching: {str(e)}")
            raise StyleMatchingError(f"Style matching failed: {str(e)}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the status of the style matching agent"""
        return {
            "agent_type": "style_matching",
            "status": "active",
            "model": "gemini-2.5-flash",
            "capabilities": [
                "similarity_analysis",
                "style_analysis", 
                "content_adaptation",
                "length_enforcement"
            ],
            "supported_platforms": ["twitter", "linkedin"],
            "max_context_posts": 10,
            "similarity_algorithm": "sequence_matcher"
        } 