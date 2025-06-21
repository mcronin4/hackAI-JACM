from app.agents.topic_extractor import TopicExtractorAgent
from app.models import Topic, TopicExtractionResponse
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class TopicExtractionService:
    def __init__(self):
        # Initialize the agent with configuration from environment
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
        temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.1"))
        
        self.agent = TopicExtractorAgent(
            model_name=model_name,
            temperature=temperature
        )
    
    async def extract_topics(self, text: str, max_topics: int = 10) -> TopicExtractionResponse:
        """
        Extract topics from text using the LangGraph agent
        
        Args:
            text: The input text to analyze
            max_topics: Maximum number of topics to extract
            
        Returns:
            TopicExtractionResponse with extracted topics
        """
        try:
            # Validate input
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            if max_topics < 1 or max_topics > 50:
                raise ValueError("max_topics must be between 1 and 50")
            
            # Extract topics using the agent
            result = self.agent.extract_topics(text, max_topics)
            
            if not result['success']:
                raise Exception(result['error'])
            
            # Convert to Pydantic models
            topics = []
            for topic_data in result['topics']:
                topic = Topic(
                    topic_id=topic_data['topic_id'],
                    topic_name=topic_data['topic_name'],
                    content_excerpt=topic_data['content_excerpt'],
                    confidence_score=topic_data.get('confidence_score')
                )
                topics.append(topic)
            
            return TopicExtractionResponse(
                topics=topics,
                total_topics=result['total_topics'],
                processing_time=result['processing_time']
            )
            
        except Exception as e:
            # Re-raise as a more specific exception
            raise TopicExtractionError(f"Failed to extract topics: {str(e)}")
    
    def get_agent_status(self) -> dict:
        """Get the status of the topic extraction agent"""
        return {
            "status": "ready",
            "model": self.agent.llm.model,
            "temperature": self.agent.llm.temperature
        }


class TopicExtractionError(Exception):
    """Custom exception for topic extraction errors"""
    pass 