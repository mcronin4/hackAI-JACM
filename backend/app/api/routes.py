from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models import (
    ContentPipelineRequest,
    ContentPipelineResponse,
    ErrorResponse,
    TopicExtractionOnlyRequest,
    TopicExtractionOnlyResponse,
    EmotionTargetingOnlyRequest,
    EmotionTargetingOnlyResponse,
    ContentGenerationOnlyRequest,
    ContentGenerationOnlyResponse,
    YouTubeProcessRequest,
    YouTubeProcessResponse,
    PlatformPostRequest,
    PlatformPostResponse,
    PlatformStatusResponse,
    AllPlatformsStatusResponse,
    PlatformPosts,
    PlatformPost,
    TwitterContextRequest,
    TwitterContextResponse,
    AudienceExtractionOnlyRequest,
    AudienceExtractionOnlyResponse,
    StyleMatchingOnlyRequest,
    StyleMatchingOnlyResponse
)
from app.services.content_pipeline import ContentPipelineService, ContentPipelineError
from app.services.streaming_pipeline import StreamingPipelineService, StreamingPipelineError
from app.services.topic_service import TopicExtractionService, TopicExtractionError
from app.services.emotion_service import EmotionTargetingService, EmotionTargetingError
from app.services.content_generation_service import ContentGenerationOnlyService, ContentGenerationOnlyError
from app.services.youtube_service import YouTubeService, YouTubeConversionError
from app.services.social_posting_service import SocialPostingService
from app.services.social_media.base_platform import PostRequest
from app.services.social_media.platform_factory import PlatformFactory
from app.services.user_context_service import UserContextService, UserContextError
from app.services.audience_service import AudienceExtractionService, AudienceExtractionError
from app.services.style_matching_service import StyleMatchingService, StyleMatchingError
from typing import Dict, Any
import logging
import json
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["content-pipeline"])


def get_pipeline_service() -> ContentPipelineService:
    """Dependency injection for content pipeline service"""
    return ContentPipelineService()


def get_streaming_pipeline_service() -> StreamingPipelineService:
    """Dependency injection for streaming pipeline service"""
    return StreamingPipelineService()


def get_topic_service() -> TopicExtractionService:
    """Dependency injection for topic extraction service"""
    return TopicExtractionService()


def get_social_posting_service() -> SocialPostingService:
    """Dependency injection for social posting service"""
    return SocialPostingService()

def get_emotion_service() -> EmotionTargetingService:
    """Dependency injection for emotion targeting service"""
    return EmotionTargetingService()


def get_content_service() -> ContentGenerationOnlyService:
    """Dependency injection for content generation service"""
    return ContentGenerationOnlyService()


def get_user_context_service() -> UserContextService:
    """Dependency injection for user context service"""
    return UserContextService()


def get_audience_service() -> AudienceExtractionService:
    """Dependency injection for audience extraction service"""
    return AudienceExtractionService()


def get_style_matching_service() -> StyleMatchingService:
    """Dependency injection for style matching service"""
    return StyleMatchingService()


# INDIVIDUAL AGENT ENDPOINTS
def get_youtube_service() -> YouTubeService:
    """Dependency injection for YouTube conversion service"""
    return YouTubeService()

@router.post(
    "/extract-topics",
    response_model=TopicExtractionOnlyResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Extract topics from text",
    description="Extract topics from input text using the topic extraction agent only"
)
async def extract_topics_only(
    request: TopicExtractionOnlyRequest,
    topic_service: TopicExtractionService = Depends(get_topic_service)
) -> TopicExtractionOnlyResponse:
    """
    Extract topics from text using only the topic extraction agent.
    This endpoint allows you to test the topic extraction functionality independently.
    """
    try:
        logger.info(f"Processing topic extraction request for {len(request.text)} characters of text")
        
        result = await topic_service.extract_topics(
            text=request.text
        )
        
        if result.success:
            logger.info(f"Successfully extracted {result.total_topics} topics")
        else:
            logger.warning(f"Topic extraction failed: {result.error}")
        
        return result
        
    except TopicExtractionError as e:
        logger.error(f"Topic extraction error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Topic extraction failed",
                "detail": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in topic extraction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during topic extraction"
            }
        )


@router.post(
    "/analyze-emotions",
    response_model=EmotionTargetingOnlyResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Analyze emotions for topics",
    description="Analyze emotional themes for a list of topics using the emotion targeting agent only"
)
async def analyze_emotions_only(
    request: EmotionTargetingOnlyRequest,
    emotion_service: EmotionTargetingService = Depends(get_emotion_service)
) -> EmotionTargetingOnlyResponse:
    """
    Analyze emotions for a list of topics using only the emotion targeting agent.
    This endpoint allows you to test the emotion analysis functionality independently.
    """
    try:
        logger.info(f"Processing emotion analysis request for {len(request.topics)} topics")
        
        result = await emotion_service.analyze_emotions(topics=request.topics)
        
        if result.success:
            logger.info(f"Successfully analyzed emotions for {result.total_topics} topics")
        else:
            logger.warning(f"Emotion analysis failed: {result.error}")
        
        return result
        
    except EmotionTargetingError as e:
        logger.error(f"Emotion targeting error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Emotion analysis failed",
                "detail": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in emotion analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during emotion analysis"
            }
        )


@router.post(
    "/generate-content",
    response_model=ContentGenerationOnlyResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate social media content",
    description="Generate social media content for enhanced topics using the content generation agent only"
)
async def generate_content_only(
    request: ContentGenerationOnlyRequest,
    content_service: ContentGenerationOnlyService = Depends(get_content_service)
) -> ContentGenerationOnlyResponse:
    """
    Generate social media content for enhanced topics using only the content generation agent.
    This endpoint allows you to test the content generation functionality independently.
    """
    try:
        logger.info(f"Processing content generation request for {len(request.topics)} topics and {len(request.target_platforms)} platforms")
        
        result = await content_service.generate_content(
            original_text=request.original_text,
            topics=request.topics,
            original_url=request.original_url,
            audience_context=request.audience_context,
            target_platforms=request.target_platforms
        )
        
        if result.success:
            logger.info(f"Successfully generated {result.successful_generations} content pieces out of {result.total_generated}")
        else:
            logger.warning(f"Content generation failed: {result.error}")
        
        return result
        
    except ContentGenerationOnlyError as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Content generation failed",
                "detail": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in content generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during content generation"
            }
        )


# UNIFIED PIPELINE ENDPOINT (existing)

@router.post(
    "/generate-posts",
    response_model=ContentPipelineResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate social media posts from text",
    description="Process text through the complete pipeline: extract topics → analyze emotions → generate content"
)
async def generate_posts(
    request: ContentPipelineRequest,
    pipeline_service: ContentPipelineService = Depends(get_pipeline_service)
) -> ContentPipelineResponse:
    """
    Generate social media posts from text using the unified pipeline. This will start by gathering context posts from the database if a user was specified.
    
    The pipeline will:
    1. Extract topics from the input text
    2. Analyze emotional themes for each topic
    3. Generate platform-specific content for each topic
    4. Return a list of ready-to-post content
    """
    try:
        logger.info(f"Processing pipeline request for {len(request.text)} characters of text")

        context_posts = {}
        if request.user_id:
            for platform in request.target_platforms:
                platform_context = await pipeline_service.get_user_context_posts(request.user_id, platform)
                context_posts[platform] = sorted([post["post_content"] for post in platform_context], key=len, reverse=True)[:10] # Sort by length and take the longest 10
        
        result = await pipeline_service.process_content(
            text=request.text,
            original_url=request.original_url,
            context_posts=context_posts,
            target_platforms=request.target_platforms
        )
        
        if result['success']:            
            # Create platform-separated posts structure
            platform_posts = PlatformPosts()
            
            # Use the platform_posts from the pipeline service result
            if 'platform_posts' in result:
                pipeline_platform_posts = result['platform_posts']
                
                # Convert Twitter posts
                if 'twitter' in pipeline_platform_posts:
                    for post_data in pipeline_platform_posts['twitter']:
                        platform_post = PlatformPost(
                            post_content=post_data.get('post_content', ''),
                            topic_id=post_data.get('topic_id', 0),
                            topic_name=post_data.get('topic_name', ''),
                            primary_emotion=post_data.get('primary_emotion', ''),
                            content_strategy=post_data.get('content_strategy', 'single_tweet'),
                            processing_time=post_data.get('processing_time', 0.0)
                        )
                        platform_posts.twitter.append(platform_post)
                
                # Convert LinkedIn posts
                if 'linkedin' in pipeline_platform_posts:
                    for post_data in pipeline_platform_posts['linkedin']:
                        platform_post = PlatformPost(
                            post_content=post_data.get('post_content', ''),
                            topic_id=post_data.get('topic_id', 0),
                            topic_name=post_data.get('topic_name', ''),
                            primary_emotion=post_data.get('primary_emotion', ''),
                            content_strategy=post_data.get('content_strategy', 'professional_post'),
                            processing_time=post_data.get('processing_time', 0.0)
                        )
                        platform_posts.linkedin.append(platform_post)
            
            return ContentPipelineResponse(
                success=True,
                platform_posts=platform_posts,
                generated_posts=result['generated_posts'],
                total_topics=result['total_topics'],
                successful_generations=result['successful_generations'],
                processing_time=result['processing_time'],
                pipeline_details=result.get('pipeline_details')
            )
        else:
            logger.warning(f"Pipeline processing failed: {result['error']}")
            
            return ContentPipelineResponse(
                success=False,
                platform_posts=PlatformPosts(),  # Empty platform posts
                generated_posts=[],
                total_topics=result['total_topics'],
                successful_generations=result['successful_generations'],
                processing_time=result['processing_time'],
                error=result['error']
            )
        
    except ContentPipelineError as e:
        logger.error(f"Content pipeline error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Content pipeline processing failed",
                "detail": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in pipeline processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during pipeline processing"
            }
        )


# UTILITY ENDPOINTS

@router.post(
    "/youtube/process",
    response_model=YouTubeProcessResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid YouTube URL or processing failed"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Process YouTube Video to Audio and Transcript",
    description="Accepts a YouTube URL, downloads the audio, converts it to MP3, and generates a transcript."
)
async def process_youtube_video(
    request: YouTubeProcessRequest,
    youtube_service: YouTubeService = Depends(get_youtube_service)
) -> YouTubeProcessResponse:
    """
    This endpoint orchestrates the entire process:
    1.  Takes a YouTube URL.
    2.  Uses `yt-dlp` to download the best audio stream.
    3.  Converts the audio to an MP3 file.
    4.  Uses Deepgram to transcribe the MP3.
    5.  Returns the transcript and other metadata.
    """
    try:
        logger.info(f"Received request to process YouTube URL: {request.url}")
        
        # The youtube_service.convert_to_mp3 now handles the entire pipeline
        result = youtube_service.convert_to_mp3(request.url)
        
        if not result.get("success"):
            # Raise an HTTPException to be caught and returned as a proper error response
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "An unknown error occurred during processing.")
            )

        logger.info(f"Successfully processed video: {result.get('video_title')}")
        
        return YouTubeProcessResponse(
            success=True,
            video_id=result.get("video_id"),
            video_title=result.get("video_title"),
            video_duration=result.get("video_duration"),
            mp3_file_path=result.get("audio_stream", {}).get("url"),
            transcript=result.get("transcript"),
            processing_time_seconds=result.get("processing_time"),
            error_message=None
        )
        
    except YouTubeConversionError as e:
        logger.error(f"A known error occurred during YouTube processing: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected server error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


async def get_supported_platforms(
    pipeline_service: ContentPipelineService = Depends(get_pipeline_service)
) -> Dict[str, Any]:
    """Get list of supported social media platforms and their configurations"""
    try:
        status = pipeline_service.get_pipeline_status()
        return {
            "supported_platforms": status['agents']['content_generator']['supported_platforms'],
            "default_platform": "twitter",
            "platform_details": {
                "twitter": {
                    "max_length": 280,
                    "url_length": 23,
                    "supports_threads": False
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get platform information: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve platform information",
                "detail": str(e)
            }
        )

@router.get(
    "/youtube/example",
    summary="Get YouTube conversion example",
    description="Get an example of the YouTube conversion response format"
)
async def get_youtube_example_response() -> YouTubeProcessResponse:
    """Return an example response to show the expected YouTube conversion format"""
    from app.models import AudioStream
    
    return YouTubeProcessResponse(
        success=True,
        video_id="dQw4w9WgXcQ",
        video_title="Rick Astley - Never Gonna Give You Up (Official Music Video)",
        video_duration="3:33",
        mp3_file_path="https://example.com/audio.mp3",
        processing_time_seconds=2.45,
        error_message=None
    )


@router.get(
    "/youtube/status",
    summary="YouTube Service Status",
    description="Check the status of the local YouTube processing service (yt-dlp)."
)
async def youtube_service_status(
    youtube_service: YouTubeService = Depends(get_youtube_service)
) -> Dict[str, Any]:
    """Get the status of the YouTube conversion service"""
    return youtube_service.get_service_status()


@router.get(
    "/health",
    summary="Health check",
    description="Check if all services are healthy"
)
async def health_check(
    pipeline_service: ContentPipelineService = Depends(get_pipeline_service),
    topic_service: TopicExtractionService = Depends(get_topic_service),
    emotion_service: EmotionTargetingService = Depends(get_emotion_service),
    content_service: ContentGenerationOnlyService = Depends(get_content_service),
    audience_service: AudienceExtractionService = Depends(get_audience_service),
    style_service: StyleMatchingService = Depends(get_style_matching_service)
) -> Dict[str, Any]:
    """Health check endpoint to verify all service statuses"""
    try:
        return {
            "status": "healthy",
            "service": "content-pipeline-api",
            "agents": {
                "audience_extractor": audience_service.get_agent_status(),
                "topic_extractor": topic_service.get_agent_status(),
                "emotion_targeting": emotion_service.get_agent_status(),
                "content_generator": content_service.get_agent_status(),
                "style_matcher": style_service.get_agent_status(),
                "pipeline": pipeline_service.get_pipeline_status()
            },
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service unhealthy",
                "detail": str(e)
            }
        )

@router.get(
    "/pipeline/example",
    summary="Get example request",
    description="Get an example of the pipeline request format"
)
async def get_example_request() -> ContentPipelineRequest:
    """Return an example request to show the expected format"""
    return ContentPipelineRequest(
        text="Artificial intelligence is revolutionizing how we work and live. "
             "Machine learning algorithms are becoming more sophisticated, "
             "enabling new applications across industries. From healthcare to finance, "
             "AI is creating opportunities for innovation and efficiency. "
             "However, it also raises important questions about the future of work "
             "and the need for new skills in the digital economy.",
        original_url="https://example.com/ai-future-article",
        target_platforms=["twitter"]
    )


@router.get(
    "/pipeline/platforms",
    summary="Get supported platforms",
    description="Get list of supported social media platforms"
)
async def get_supported_platforms(
    pipeline_service: ContentPipelineService = Depends(get_pipeline_service)
) -> Dict[str, Any]:
    """Get list of supported social media platforms and their configurations"""
    try:
        status = pipeline_service.get_pipeline_status()
        return {
            "supported_platforms": status['agents']['content_generator']['supported_platforms'],
            "default_platform": "twitter",
            "platform_details": {
                "twitter": {
                    "max_length": 280,
                    "url_length": 23,
                    "supports_threads": False
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get platform information: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve platform information",
                "detail": str(e)
            }
        )

@router.get(
    "/youtube/example",
    summary="Get YouTube conversion example",
    description="Get an example of the YouTube conversion response format"
)
async def get_youtube_example_response() -> YouTubeProcessResponse:
    """Return an example response to show the expected YouTube conversion format"""
    from app.models import AudioStream
    
    return YouTubeProcessResponse(
        success=True,
        video_id="dQw4w9WgXcQ",
        video_title="Rick Astley - Never Gonna Give You Up (Official Music Video)",
        video_duration="3:33",
        mp3_file_path="https://example.com/audio.mp3",
        processing_time_seconds=2.45,
        error_message=None
    )


# Social Media Posting Endpoints

@router.post(
    "/post/{platform}",
    response_model=PlatformPostResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Post to specific social media platform",
    description="Post content to a specific social media platform (twitter, linkedin, etc.)"
)
async def post_to_platform(
    platform: str,
    request: PlatformPostRequest,
    posting_service: SocialPostingService = Depends(get_social_posting_service)
) -> PlatformPostResponse:
    """
    Post content to a specific social media platform.
    
    Supported platforms:
    - twitter: Post tweets (280 character limit)
    - linkedin: Post to LinkedIn feed (3000 character limit)
    """
    try:
        logger.info(f"Posting to {platform} with content length: {len(request.content)}")
        
        post_request = PostRequest(
            content=request.content,
            thread_id=request.thread_id
        )
        
        result = await posting_service.post_to_platform(platform, post_request)
        
        if result.success:
            logger.info(f"Successfully posted to {platform}. Post ID: {result.post_id}")
        else:
            logger.error(f"Failed to post to {platform}: {result.error}")
        
        return PlatformPostResponse(
            success=result.success,
            platform=result.platform,
            post_id=result.post_id,
            post_url=result.post_url,
            error=result.error,
            posted_at=result.posted_at
        )
        
    except Exception as e:
        logger.error(f"Unexpected error posting to {platform}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during posting"
            }
        )


@router.get(
    "/platforms",
    summary="Get supported platforms",
    description="Get list of all supported social media platforms"
)
async def get_supported_platforms():
    """Get list of supported social media platforms"""
    return {
        "platforms": PlatformFactory.get_supported_platforms(),
        "total": len(PlatformFactory.get_supported_platforms())
    }


@router.get(
    "/platforms/{platform}/status",
    response_model=PlatformStatusResponse,
    summary="Get platform status",
    description="Get configuration and credential status for a specific platform"
)
async def get_platform_status(
    platform: str,
    posting_service: SocialPostingService = Depends(get_social_posting_service)
) -> PlatformStatusResponse:
    """Get status information for a specific platform"""
    try:
        status = posting_service.get_platform_status(platform)
        return PlatformStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting status for {platform}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred getting platform status"
            }
        )


@router.get(
    "/platforms/status",
    response_model=AllPlatformsStatusResponse,
    summary="Get all platforms status",
    description="Get configuration and credential status for all supported platforms"
)
async def get_all_platforms_status(
    posting_service: SocialPostingService = Depends(get_social_posting_service)
) -> AllPlatformsStatusResponse:
    """Get status information for all supported platforms"""
    try:
        status = posting_service.get_all_platforms_status()
        return AllPlatformsStatusResponse(platforms=status)
    except Exception as e:
        logger.error(f"Error getting platforms status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred getting platforms status"
            }
        )

@router.post(
    "/stream-posts",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Stream social media posts as they're generated",
    description="Stream social media posts as they're generated through the pipeline"
)
async def stream_posts(
    request: ContentPipelineRequest,
    streaming_pipeline_service: StreamingPipelineService = Depends(get_streaming_pipeline_service)
):
    """
    Stream social media posts as they're generated through the pipeline.
    
    This endpoint uses Server-Sent Events (SSE) to stream posts as they're generated.
    """
    try:
        logger.info(f"Processing stream request for {len(request.text)} characters of text")
        
        async def generate_posts_stream():
            async for event in streaming_pipeline_service.stream_posts(
                text=request.text,
                original_url=request.original_url,
                target_platforms=request.target_platforms
            ):
                yield event
        
        return StreamingResponse(
            generate_posts_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except StreamingPipelineError as e:
        logger.error(f"Streaming pipeline error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Streaming pipeline processing failed",
                "detail": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in streaming pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during streaming pipeline processing"
            }
        ) 