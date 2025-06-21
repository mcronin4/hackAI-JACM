from fastapi import APIRouter, HTTPException, Depends
from app.models import (
    TopicExtractionRequest, 
    TopicExtractionResponse, 
    ContentGenerationRequest,
    ContentGenerationResponse,
    ErrorResponse
)
from app.services.topic_service import TopicExtractionService, TopicExtractionError
from app.services.content_service import ContentGenerationService, ContentGenerationError
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["topic-extraction", "content-generation"])


def get_topic_service() -> TopicExtractionService:
    """Dependency injection for topic extraction service"""
    return TopicExtractionService()


def get_content_service() -> ContentGenerationService:
    """Dependency injection for content generation service"""
    return ContentGenerationService()


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


@router.post(
    "/generate-content",
    response_model=ContentGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Generate social media content from topics",
    description="Use LangGraph agent to generate platform-specific content from enhanced topics with emotion data"
)
async def generate_content(
    request: ContentGenerationRequest,
    content_service: ContentGenerationService = Depends(get_content_service)
) -> ContentGenerationResponse:
    """
    Generate social media content from enhanced topics with emotion data.
    
    The agent will:
    - Process each topic independently
    - Generate platform-specific content (starting with Twitter/X)
    - Create engaging content based on emotional context
    - Add relevant hashtags and call-to-action
    - Include links back to original content
    """
    try:
        logger.info(f"Processing content generation request for {len(request.topics)} topics and {len(request.target_platforms)} platforms")
        
        response = await content_service.generate_content(
            original_text=request.original_text,
            topics=request.topics,
            original_url=request.original_url,
            target_platforms=request.target_platforms
        )
        
        logger.info(f"Successfully generated {response.successful_generations}/{response.total_generated} content pieces")
        return response
        
    except ContentGenerationError as e:
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


@router.get(
    "/platforms",
    summary="Get supported platforms",
    description="Get list of supported social media platforms and their configurations"
)
async def get_supported_platforms(
    content_service: ContentGenerationService = Depends(get_content_service)
) -> Dict[str, Any]:
    """Get supported platforms and their configurations"""
    try:
        status = content_service.get_agent_status()
        platforms = {}
        
        for platform in status['supported_platforms']:
            try:
                config = content_service.get_platform_config(platform)
                platforms[platform] = config
            except Exception as e:
                logger.warning(f"Could not get config for platform {platform}: {str(e)}")
        
        return {
            "platforms": status['supported_platforms'],
            "supported_platforms": status['supported_platforms'],
            "platform_configs": platforms,
            "agent_status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting platform information: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get platform information",
                "detail": str(e)
            }
        )


@router.get(
    "/content/example",
    summary="Get example content generation request",
    description="Get an example of the content generation request format"
)
async def get_example_content_request() -> ContentGenerationRequest:
    """Return an example request to show the expected format"""
    from app.models import EnhancedTopic
    
    example_topics = [
        EnhancedTopic(
            topic_id=1,
            topic_name="Remote Work Productivity Challenges",
            content_excerpt="Many professionals struggle with distractions when working from home, leading to decreased productivity and increased stress levels.",
            primary_emotion="Justify Their Failures",
            emotion_confidence=0.85,
            reasoning="This topic validates the common struggle with remote work productivity, allowing the audience to feel understood rather than blamed for their challenges."
        ),
        EnhancedTopic(
            topic_id=2,
            topic_name="AI Tools for Productivity",
            content_excerpt="Artificial intelligence tools are revolutionizing how we approach daily tasks and workflow optimization.",
            primary_emotion="Anticipation",
            emotion_confidence=0.92,
            reasoning="This topic creates excitement about future possibilities and technological advancement in workplace efficiency."
        )
    ]
    
    return ContentGenerationRequest(
        original_text="Long-form article about remote work challenges and AI solutions for modern professionals...",
        topics=example_topics,
        original_url="https://example.com/remote-work-ai-productivity",
        target_platforms=["twitter"]
    ) 