from fastapi import APIRouter, HTTPException, Depends
from app.models import (
    TopicExtractionRequest, 
    TopicExtractionResponse, 
    ErrorResponse
)
from app.services.topic_service import TopicExtractionService, TopicExtractionError
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["topic-extraction"])


def get_topic_service() -> TopicExtractionService:
    """Dependency injection for topic extraction service"""
    return TopicExtractionService()


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