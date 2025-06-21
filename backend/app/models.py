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
class YouTubeConversionRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL to convert to MP3")


class AudioStream(BaseModel):
    url: Optional[str] = Field(None, description="Direct download URL for the audio file")
    quality: Optional[str] = Field(None, description="Audio quality (e.g., 128kbps, 320kbps)")
    format: Optional[str] = Field(None, description="Audio format (e.g., mp3, m4a)")
    size: Optional[str] = Field(None, description="File size in bytes or human-readable format")


class YouTubeConversionResponse(BaseModel):
    success: bool = Field(..., description="Whether the conversion was successful")
    video_id: Optional[str] = Field(None, description="YouTube video ID")
    video_title: Optional[str] = Field(None, description="Title of the YouTube video")
    video_duration: Optional[str] = Field(None, description="Duration of the video")
    audio_stream: Optional[AudioStream] = Field(None, description="Audio stream information")
    transcript: Optional[str] = Field(None, description="The full transcript of the video audio")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    timestamp: str = Field(..., description="ISO timestamp of when the request was processed")
    error: Optional[str] = Field(None, description="Error message if conversion failed") 