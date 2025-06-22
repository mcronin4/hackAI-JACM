from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class TopicExtractionRequest(BaseModel):
    text: str = Field(..., description="The text content to extract topics from")


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
    emotion_description: str = Field(..., description="Description of what this emotion represents")
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


# New models for the unified pipeline API
class ContentPipelineRequest(BaseModel):
    """Request for the unified content processing pipeline"""
    text: str = Field(..., description="The original text to process")
    original_url: str = Field(..., description="URL of the original content")
    target_platforms: Optional[List[str]] = Field(
        default=["twitter"], 
        description="Target social media platforms"
    )


class ContentPipelineResponse(BaseModel):
    """Response from the unified content processing pipeline"""
    success: bool = Field(..., description="Whether the pipeline processing was successful")
    generated_posts: List[str] = Field(..., description="List of generated social media posts")
    total_topics: int = Field(..., description="Number of topics that were processed")
    successful_generations: int = Field(..., description="Number of successful content generations")
    processing_time: float = Field(..., description="Total processing time in seconds")
    pipeline_details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional details about the pipeline processing"
    )
    error: Optional[str] = Field(None, description="Error message if processing failed")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


# Individual Agent Models for separate endpoints
class TopicExtractionOnlyRequest(BaseModel):
    """Request for topic extraction only"""
    text: str = Field(..., description="The text content to extract topics from")


class TopicExtractionOnlyResponse(BaseModel):
    """Response from topic extraction only"""
    success: bool = Field(..., description="Whether the extraction was successful")
    topics: List[Topic] = Field(..., description="List of extracted topics")
    total_topics: int = Field(..., description="Total number of topics extracted")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    error: Optional[str] = Field(None, description="Error message if extraction failed")


class EmotionTargetingOnlyRequest(BaseModel):
    """Request for emotion targeting only"""
    topics: List[Topic] = Field(..., description="List of topics to analyze for emotions")


class EmotionTargetingOnlyResponse(BaseModel):
    """Response from emotion targeting only"""
    success: bool = Field(..., description="Whether the emotion analysis was successful")
    enhanced_topics: List[EnhancedTopic] = Field(..., description="List of topics with emotion data")
    total_topics: int = Field(..., description="Total number of topics processed")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


class ContentGenerationOnlyRequest(BaseModel):
    """Request for content generation only"""
    original_text: str = Field(..., description="The original long-form text")
    topics: List[EnhancedTopic] = Field(..., description="List of enhanced topics with emotion data")
    original_url: str = Field(..., description="URL of the original content")
    target_platforms: Optional[List[str]] = Field(
        default=["twitter"], 
        description="Target social media platforms"
    )


class ContentGenerationOnlyResponse(BaseModel):
    """Response from content generation only"""
    success: bool = Field(..., description="Whether the generation was successful")
    generated_content: List[GeneratedContent] = Field(..., description="List of generated content pieces")
    total_generated: int = Field(..., description="Total number of content pieces generated")
    successful_generations: int = Field(..., description="Number of successful generations")
    processing_time: float = Field(..., description="Total processing time")
    error: Optional[str] = Field(None, description="Error message if generation failed") 

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