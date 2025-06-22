from app.agents.emotion_targeting import EmotionTargetingAgent
from app.models import Topic, EnhancedTopic, EmotionTargetingOnlyResponse
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class EmotionTargetingService:
    def __init__(self):
        # Initialize the agent with configuration from environment
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
        temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.3"))
        
        self.agent = EmotionTargetingAgent(
            model_name=model_name,
            temperature=temperature
        )
    
    async def analyze_emotions(
        self, 
        topics: List[Topic]
    ) -> EmotionTargetingOnlyResponse:
        """
        Analyze emotions for a list of topics using the emotion targeting agent
        
        Args:
            topics: List of topics to analyze for emotions
            
        Returns:
            EmotionTargetingOnlyResponse with enhanced topics containing emotion data
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not topics or len(topics) == 0:
                raise ValueError("Topics list cannot be empty")
            
            # Convert Topic models to dictionaries for the agent
            topics_data = []
            for topic in topics:
                topic_dict = {
                    'topic_id': topic.topic_id,
                    'topic_name': topic.topic_name,
                    'content_excerpt': topic.content_excerpt,
                    'confidence_score': topic.confidence_score
                }
                topics_data.append(topic_dict)
            
            # Analyze emotions using the agent
            result = self.agent.analyze_emotions(topics_data)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if result['success']:
                # Convert to EnhancedTopic models
                enhanced_topics = []
                for enhanced_data in result['emotion_analysis']:
                    enhanced_topic = EnhancedTopic(
                        topic_id=enhanced_data['topic_id'],
                        topic_name=enhanced_data['topic_name'],
                        content_excerpt=enhanced_data['content_excerpt'],
                        primary_emotion=enhanced_data['primary_emotion'],
                        emotion_description=enhanced_data['emotion_description'],
                        emotion_confidence=enhanced_data['emotion_confidence'],
                        reasoning=enhanced_data['reasoning']
                    )
                    enhanced_topics.append(enhanced_topic)
                
                return EmotionTargetingOnlyResponse(
                    success=True,
                    enhanced_topics=enhanced_topics,
                    total_topics=len(enhanced_topics),
                    processing_time=processing_time
                )
            else:
                return EmotionTargetingOnlyResponse(
                    success=False,
                    enhanced_topics=[],
                    total_topics=0,
                    processing_time=processing_time,
                    error=result['error']
                )
                
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return EmotionTargetingOnlyResponse(
                success=False,
                enhanced_topics=[],
                total_topics=0,
                processing_time=processing_time,
                error=f"Failed to analyze emotions: {str(e)}"
            )
    
    def get_agent_status(self) -> dict:
        """Get the status of the emotion targeting agent"""
        return {
            "status": "ready",
            "model": self.agent.llm.model,
            "temperature": self.agent.llm.temperature,
            "agent_type": "emotion_targeting"
        }


class EmotionTargetingError(Exception):
    """Custom exception for emotion targeting errors"""
    pass 