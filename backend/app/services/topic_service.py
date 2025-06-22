from app.agents.topic_extractor import TopicExtractorAgent
from app.models import Topic, TopicExtractionOnlyResponse
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime

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
    
    async def extract_topics(
        self, 
        text: str
    ) -> TopicExtractionOnlyResponse:
        """
        Extract topics from text using the topic extraction agent
        
        Args:
            text: The text content to extract topics from
            
        Returns:
            TopicExtractionOnlyResponse with extracted topics
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Extract topics using the agent
            result = self.agent.extract_topics(text)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if result['success']:
                # Convert to Topic models
                topics = []
                for topic_data in result['topics']:
                    topic = Topic(
                        topic_id=topic_data['topic_id'],
                        topic_name=topic_data['topic_name'],
                        content_excerpt=topic_data['content_excerpt'],
                        confidence_score=topic_data.get('confidence_score', 0.8)
                    )
                    topics.append(topic)
                
                return TopicExtractionOnlyResponse(
                    success=True,
                    topics=topics,
                    total_topics=len(topics),
                    processing_time=processing_time
                )
            else:
                return TopicExtractionOnlyResponse(
                    success=False,
                    topics=[],
                    total_topics=0,
                    processing_time=processing_time,
                    error=result['error']
                )
                
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return TopicExtractionOnlyResponse(
                success=False,
                topics=[],
                total_topics=0,
                processing_time=processing_time,
                error=f"Failed to extract topics: {str(e)}"
            )
    
    def get_agent_status(self) -> dict:
        """Get the status of the topic extraction agent"""
        return {
            "status": "ready",
            "model": self.agent.llm.model,
            "temperature": self.agent.llm.temperature,
            "agent_type": "topic_extractor"
        }


class TopicExtractionError(Exception):
    """Custom exception for topic extraction errors"""
    pass 