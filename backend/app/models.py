from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class TopicExtractionRequest(BaseModel):
    text: str = Field(..., description="The text content to extract topics from")
    max_topics: Optional[int] = Field(10, description="Maximum number of topics to extract")


class Topic(BaseModel):
    topic_id: int = Field(..., description="Unique identifier for the topic")
    topic_name: str = Field(..., description="Name/description of the topic")
    content_excerpt: str = Field(..., description="Relevant excerpt from the content")
    confidence_score: Optional[float] = Field(None, description="Confidence score for the topic extraction")


class TopicExtractionResponse(BaseModel):
    topics: List[Topic] = Field(..., description="List of extracted topics")
    total_topics: int = Field(..., description="Total number of topics extracted")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")


class EnhancedTopic(BaseModel):
    """Enhanced topic with emotion and reasoning data"""
    topic_id: int = Field(..., description="Unique identifier for the topic")
    topic_name: str = Field(..., description="Name/description of the topic")
    content_excerpt: str = Field(..., description="Relevant excerpt from the content")
    primary_emotion: str = Field(..., description="Primary emotion detected for this topic")
    emotion_confidence: float = Field(..., description="Confidence score for emotion detection")
    reasoning: str = Field(..., description="Reasoning behind the emotion classification")


class ContentGenerationRequest(BaseModel):
    """Request for content generation"""
    original_text: str = Field(..., description="The original long-form text")
    topics: List[EnhancedTopic] = Field(..., description="List of enhanced topics with emotion data")
    original_url: str = Field(..., description="URL of the original content")
    target_platforms: List[str] = Field(default=["twitter"], description="Target social media platforms")


class GeneratedContent(BaseModel):
    """Generated content for a specific topic and platform"""
    topic_id: int = Field(..., description="ID of the topic this content was generated for")
    platform: str = Field(..., description="Platform this content was generated for")
    final_post: str = Field(..., description="Final formatted post content")
    content_strategy: str = Field(..., description="Strategy used (e.g., single_tweet, thread)")
    hashtags: List[str] = Field(default=[], description="Generated hashtags")
    call_to_action: str = Field(..., description="Generated call to action")
    success: bool = Field(..., description="Whether generation was successful")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    processing_time: float = Field(..., description="Time taken to generate this content")


class ContentGenerationResponse(BaseModel):
    """Response from content generation"""
    generated_content: List[GeneratedContent] = Field(..., description="List of generated content pieces")
    total_generated: int = Field(..., description="Total number of content pieces generated")
    successful_generations: int = Field(..., description="Number of successful generations")
    total_processing_time: float = Field(..., description="Total processing time")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details") 