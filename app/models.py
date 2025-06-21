from pydantic import BaseModel, Field
from typing import List, Optional
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


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details") 