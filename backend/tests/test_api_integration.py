import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import asyncio
import sys
import os

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the problematic imports before importing the app
mock_topic_extractor = Mock()
mock_emotion_analyzer = Mock()
mock_content_generator = Mock()

with patch('app.agents.topic_extractor.TopicExtractorAgent', mock_topic_extractor), \
     patch('app.agents.emotion_targeting.EmotionTargetingAgent', mock_emotion_analyzer), \
     patch('app.agents.content_generator.ContentGeneratorAgent', mock_content_generator):
    
    from app.services.content_pipeline import ContentPipelineService
    from fastapi import FastAPI
    from app.api.routes import router
    from app.models import ContentPipelineRequest, ContentPipelineResponse

# Create the FastAPI app for testing
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestContentPipelineAPI:
    """Integration tests for the unified content pipeline API"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create mock responses for the agents
        self.mock_topic_result = {
            'success': True,
            'topics': [
                {
                    'topic_id': 1,
                    'topic_name': 'Artificial Intelligence',
                    'content_excerpt': 'AI is revolutionizing the way we work',
                    'confidence_score': 0.9
                },
                {
                    'topic_id': 2,
                    'topic_name': 'Future of Work',
                    'content_excerpt': 'revolutionizing the way we work and live',
                    'confidence_score': 0.8
                }
            ],
            'total_topics': 2,
            'processing_time': 0.5
        }
        
        self.mock_emotion_result = {
            'success': True,
            'emotion_analysis': [
                {
                    'topic_id': 1,
                    'topic_name': 'Artificial Intelligence',
                    'content_excerpt': 'AI is revolutionizing the way we work',
                    'primary_emotion': 'encourage_dreams',
                    'emotion_confidence': 0.85,
                    'reasoning': 'This topic inspires future possibilities and growth'
                },
                {
                    'topic_id': 2,
                    'topic_name': 'Future of Work',
                    'content_excerpt': 'revolutionizing the way we work and live',
                    'primary_emotion': 'allay_fears',
                    'emotion_confidence': 0.75,
                    'reasoning': 'This topic addresses concerns about workplace changes'
                }
            ],
            'total_analyzed': 2,
            'processing_time': 0.8
        }
        
        self.mock_content_results = [
            {
                'topic_id': 1,
                'platform': 'twitter',
                'final_post': 'AI is transforming our world! Discover how artificial intelligence is creating new opportunities for growth and innovation. Ready to embrace the future? https://example.com/ai-article',
                'content_strategy': 'single_tweet',
                'hashtags': [],
                'call_to_action': 'Ready to embrace the future?',
                'success': True,
                'error': None,
                'processing_time': 1.2
            },
            {
                'topic_id': 2,
                'platform': 'twitter',
                'final_post': 'The future of work is here, and it\'s more exciting than scary! Learn how technology is creating better opportunities for everyone. Join the revolution! https://example.com/ai-article',
                'content_strategy': 'single_tweet',
                'hashtags': [],
                'call_to_action': 'Join the revolution!',
                'success': True,
                'error': None,
                'processing_time': 1.1
            }
        ]

    def test_generate_posts_success_full_flow(self):
        """Test successful API call with full pipeline"""
        with patch.object(ContentPipelineService, 'process_content') as mock_process:
            # Mock the pipeline service response
            mock_process.return_value = {
                'success': True,
                'generated_posts': [
                    self.mock_content_results[0]['final_post'],
                    self.mock_content_results[1]['final_post']
                ],
                'total_topics': 2,
                'successful_generations': 2,
                'processing_time': 2.5,
                'pipeline_details': {
                    'topic_extraction_time': 0.5,
                    'emotion_analysis_time': 0.8,
                    'platforms_processed': ['twitter']
                }
            }
            
            # Make API request
            request_data = {
                "text": "Artificial intelligence is revolutionizing how we work and live.",
                "original_url": "https://example.com/ai-article",
                "max_topics": 5,
                "target_platforms": ["twitter"]
            }
            
            response = client.post("/api/v1/generate-posts", json=request_data)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            assert data['success'] is True
            assert len(data['generated_posts']) == 2
            assert data['total_topics'] == 2
            assert data['successful_generations'] == 2
            assert data['processing_time'] > 0
            assert data['pipeline_details'] is not None
            
            # Verify posts contain expected content
            posts = data['generated_posts']
            assert 'AI is transforming our world!' in posts[0]
            assert 'future of work is here' in posts[1]

    def test_generate_posts_with_minimal_input(self):
        """Test API call with minimal required input"""
        with patch.object(ContentPipelineService, 'process_content') as mock_process:
            # Mock the pipeline service response
            mock_process.return_value = {
                'success': True,
                'generated_posts': [self.mock_content_results[0]['final_post']],
                'total_topics': 1,
                'successful_generations': 1,
                'processing_time': 1.5,
                'pipeline_details': {
                    'topic_extraction_time': 0.3,
                    'emotion_analysis_time': 0.4,
                    'platforms_processed': ['twitter']
                }
            }
            
            # Make API request with minimal data
            request_data = {
                "text": "Short article about AI.",
                "original_url": "https://example.com/short-ai"
            }
            
            response = client.post("/api/v1/generate-posts", json=request_data)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            assert data['success'] is True
            assert len(data['generated_posts']) == 1
            assert data['total_topics'] == 1

    def test_generate_posts_pipeline_failure(self):
        """Test API response when pipeline processing fails"""
        with patch.object(ContentPipelineService, 'process_content') as mock_process:
            # Mock pipeline failure
            mock_process.return_value = {
                'success': False,
                'error': 'Topic extraction failed: No valid topics found',
                'generated_posts': [],
                'total_topics': 0,
                'successful_generations': 0,
                'processing_time': 0.1
            }
            
            # Make API request
            request_data = {
                "text": "Invalid text that causes processing to fail.",
                "original_url": "https://example.com/invalid"
            }
            
            response = client.post("/api/v1/generate-posts", json=request_data)
            
            # Verify response
            assert response.status_code == 200  # Pipeline errors return 200 with error in response
            data = response.json()
            
            assert data['success'] is False
            assert 'Topic extraction failed' in data['error']
            assert data['generated_posts'] == []
            assert data['total_topics'] == 0

    def test_generate_posts_invalid_input(self):
        """Test API validation for invalid input"""
        # Test missing required field
        request_data = {
            "text": "Some text"
            # Missing original_url
        }
        
        response = client.post("/api/v1/generate-posts", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test empty text
        request_data = {
            "text": "",
            "original_url": "https://example.com/test"
        }
        
        response = client.post("/api/v1/generate-posts", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        with patch.object(ContentPipelineService, 'get_pipeline_status') as mock_status:
            mock_status.return_value = {
                'status': 'ready',
                'agents': {
                    'topic_extractor': {'model': 'gemini-2.5-flash', 'temperature': 0.1},
                    'emotion_analyzer': {'model': 'gemini-2.5-flash', 'temperature': 0.1},
                    'content_generator': {
                        'model': 'gemini-2.5-flash', 
                        'temperature': 0.3,
                        'supported_platforms': ['twitter']
                    }
                }
            }
            
            response = client.get("/api/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['status'] == 'healthy'
            assert data['service'] == 'content-pipeline-api'
            assert 'pipeline' in data

    def test_example_request_endpoint(self):
        """Test the example request endpoint"""
        response = client.get("/api/v1/pipeline/example")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'text' in data
        assert 'original_url' in data
        assert 'max_topics' in data
        assert 'target_platforms' in data
        assert data['max_topics'] == 3
        assert data['target_platforms'] == ['twitter']

    def test_supported_platforms_endpoint(self):
        """Test the supported platforms endpoint"""
        with patch.object(ContentPipelineService, 'get_pipeline_status') as mock_status:
            mock_status.return_value = {
                'agents': {
                    'content_generator': {
                        'supported_platforms': ['twitter', 'linkedin']
                    }
                }
            }
            
            response = client.get("/api/v1/pipeline/platforms")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'supported_platforms' in data
            assert 'default_platform' in data
            assert 'platform_details' in data
            assert data['default_platform'] == 'twitter'

    def test_content_pipeline_request_model(self):
        """Test the ContentPipelineRequest model validation"""
        # Valid request
        valid_data = {
            "text": "Test text",
            "original_url": "https://example.com",
            "max_topics": 5,
            "target_platforms": ["twitter"]
        }
        
        request = ContentPipelineRequest(**valid_data)
        assert request.text == "Test text"
        assert request.original_url == "https://example.com"
        assert request.max_topics == 5
        assert request.target_platforms == ["twitter"]
        
        # Test defaults
        minimal_data = {
            "text": "Test text",
            "original_url": "https://example.com"
        }
        
        request = ContentPipelineRequest(**minimal_data)
        assert request.max_topics == 10
        assert request.target_platforms == ["twitter"]

    def test_content_pipeline_response_model(self):
        """Test the ContentPipelineResponse model"""
        # Success response
        success_data = {
            "success": True,
            "generated_posts": ["Post 1", "Post 2"],
            "total_topics": 2,
            "successful_generations": 2,
            "processing_time": 1.5,
            "pipeline_details": {"step": "value"}
        }
        
        response = ContentPipelineResponse(**success_data)
        assert response.success is True
        assert len(response.generated_posts) == 2
        assert response.total_topics == 2
        
        # Error response
        error_data = {
            "success": False,
            "generated_posts": [],
            "total_topics": 0,
            "successful_generations": 0,
            "processing_time": 0.1,
            "error": "Processing failed"
        }
        
        response = ContentPipelineResponse(**error_data)
        assert response.success is False
        assert response.error == "Processing failed"
        assert len(response.generated_posts) == 0 