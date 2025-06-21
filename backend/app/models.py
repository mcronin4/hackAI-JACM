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


# YouTube Conversion Models
class YouTubeProcessRequest(BaseModel):
    url: str = Field(..., description="The YouTube video URL to be processed.")

class YouTubeProcessResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the entire process was successful.")
    video_id: Optional[str] = Field(None, description="The unique identifier for the YouTube video.")
    video_title: Optional[str] = Field(None, description="The title of the YouTube video.")
    video_duration: Optional[int] = Field(None, description="The duration of the video in seconds.")
    mp3_file_path: Optional[str] = Field(None, description="The local server path to the downloaded MP3 file.")
    transcript: Optional[str] = Field(None, description="The full, AI-generated transcript of the video's audio.")
    processing_time_seconds: float = Field(..., description="Total time taken for the entire process.")
    error_message: Optional[str] = Field(None, description="Details of any error that occurred.") 