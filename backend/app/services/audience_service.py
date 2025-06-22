"""Service for audience extraction operations"""

from typing import Dict, Any
import logging
from ..agents.audience_extractor import AudienceExtractorAgent

logger = logging.getLogger(__name__)

class AudienceExtractionError(Exception):
    """Custom exception for audience extraction errors"""
    pass

class AudienceExtractionService:
    """Service for extracting audience information from content"""
    
    def __init__(self):
        self.agent = AudienceExtractorAgent()
    
    async def extract_audience(self, text: str) -> Dict[str, Any]:
        """
        Extract audience information from text content
        
        Args:
            text: The original text content to analyze
            
        Returns:
            Dictionary with audience extraction results
            
        Raises:
            AudienceExtractionError: If extraction fails
        """
        try:
            logger.info(f"Starting audience extraction for {len(text)} characters")
            
            result = await self.agent.extract_audience(text)
            
            if not result['success']:
                logger.error(f"Audience extraction failed: {result['error']}")
                raise AudienceExtractionError(result['error'])
            
            logger.info(f"Successfully extracted audience in {result['processing_time']:.2f} seconds")
            return result
            
        except AudienceExtractionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in audience extraction service: {str(e)}")
            raise AudienceExtractionError(f"Audience extraction service error: {str(e)}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status information for the audience extraction agent"""
        try:
            return self.agent.get_agent_status()
        except Exception as e:
            logger.error(f"Error getting agent status: {str(e)}")
            return {
                "agent_name": "audience_extractor",
                "status": "error",
                "error": str(e)
            } 