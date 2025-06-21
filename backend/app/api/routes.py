from fastapi import APIRouter, HTTPException, Depends
from app.models import (
    TopicExtractionRequest, 
    TopicExtractionResponse, 
    ErrorResponse,
    PlatformPostRequest,
    PlatformPostResponse,
    PlatformStatusResponse,
    AllPlatformsStatusResponse
)
from app.services.topic_service import TopicExtractionService, TopicExtractionError
from app.services.social_posting_service import SocialPostingService
from app.services.social_media.base_platform import PostRequest
from app.services.social_media.platform_factory import PlatformFactory
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["topic-extraction"])


def get_topic_service() -> TopicExtractionService:
    """Dependency injection for topic extraction service"""
    return TopicExtractionService()


def get_social_posting_service() -> SocialPostingService:
    """Dependency injection for social posting service"""
    return SocialPostingService()


@router.post(
    "/extract-topics",
    response_model=TopicExtractionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Extract topics from text",
    description="Use LangGraph agent to extract topics from input text"
)
async def extract_topics(
    request: TopicExtractionRequest,
    topic_service: TopicExtractionService = Depends(get_topic_service)
) -> TopicExtractionResponse:
    """
    Extract topics from the provided text using LangGraph agent.
    
    The agent will:
    - Analyze the text for distinct topics
    - Extract relevant excerpts for each topic
    - Provide confidence scores
    - Return structured JSON response
    """
    try:
        logger.info(f"Processing topic extraction request with max_topics={request.max_topics}")
        
        response = await topic_service.extract_topics(
            text=request.text,
            max_topics=request.max_topics
        )
        
        logger.info(f"Successfully extracted {response.total_topics} topics")
        return response
        
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


@router.get(
    "/health",
    summary="Health check",
    description="Check if the topic extraction service is healthy"
)
async def health_check(
    topic_service: TopicExtractionService = Depends(get_topic_service)
) -> Dict[str, Any]:
    """Health check endpoint to verify service status"""
    try:
        agent_status = topic_service.get_agent_status()
        return {
            "status": "healthy",
            "service": "topic-extraction-api",
            "agent": agent_status,
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
    "/topics/example",
    summary="Get example response",
    description="Get an example of the topic extraction response format"
)
async def get_example_response() -> TopicExtractionResponse:
    """Return an example response to show the expected format"""
    from app.models import Topic
    
    example_topics = [
        Topic(
            topic_id=1,
            topic_name="Artificial Intelligence",
            content_excerpt="The field of artificial intelligence has seen remarkable advances in recent years, particularly in machine learning and neural networks.",
            confidence_score=0.95
        ),
        Topic(
            topic_id=2,
            topic_name="Natural Language Processing",
            content_excerpt="Natural language processing techniques enable computers to understand and generate human language effectively.",
            confidence_score=0.88
        ),
        Topic(
            topic_id=3,
            topic_name="Deep Learning",
            content_excerpt="Deep learning models have revolutionized how we approach complex pattern recognition tasks.",
            confidence_score=0.92
        )
    ]
    
    return TopicExtractionResponse(
        topics=example_topics,
        total_topics=3,
        processing_time=1.23
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