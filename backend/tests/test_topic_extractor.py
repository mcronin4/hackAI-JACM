import pytest
from unittest.mock import Mock, patch
from app.agents.topic_extractor import TopicExtractorAgent, TopicExtractionState


class TestTopicExtractorAgent:
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        mock = Mock()
        mock.invoke.return_value.content = '''[
            {
                "topic_name": "Artificial Intelligence",
                "content_excerpt": "AI has revolutionized many industries.",
                "confidence_score": 0.95
            },
            {
                "topic_name": "Machine Learning",
                "content_excerpt": "ML algorithms can learn from data.",
                "confidence_score": 0.88
            }
        ]'''
        return mock
    
    @pytest.fixture
    def agent(self, mock_llm):
        """Create agent with mocked LLM"""
        with patch('app.agents.topic_extractor.ChatGoogleGenerativeAI', return_value=mock_llm):
            return TopicExtractorAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert agent.graph is not None
    
    def test_extract_topics_node_success(self, agent):
        """Test successful topic extraction"""
        state = TopicExtractionState(
            text="AI and machine learning are transforming technology.",
            max_topics=5,
            topics=[],
            processing_time=0.0,
            error=""
        )
        
        result = agent._extract_topics_node(state)
        
        assert result['topics'] is not None
        assert len(result['topics']) == 2
        assert result['topics'][0]['topic_id'] == 1
        assert result['topics'][0]['topic_name'] == "Artificial Intelligence"
        assert result['error'] == ""
    
    def test_extract_topics_node_json_error(self, agent):
        """Test handling of JSON parsing errors"""
        # Mock LLM to return invalid JSON
        agent.llm.invoke.return_value.content = "Invalid JSON response"
        
        state = TopicExtractionState(
            text="Test text",
            max_topics=5,
            topics=[],
            processing_time=0.0,
            error=""
        )
        
        result = agent._extract_topics_node(state)
        
        assert result['error'] is not None
        assert "Could not parse JSON" in result['error']
    
    def test_validate_topics_node(self, agent):
        """Test topic validation"""
        state = TopicExtractionState(
            text="Test text",
            max_topics=5,
            topics=[
                {
                    'topic_id': 1,
                    'topic_name': 'Valid Topic',
                    'content_excerpt': 'Valid excerpt',
                    'confidence_score': 0.9
                },
                {
                    'topic_id': 2,
                    'topic_name': '',  # Invalid: empty name
                    'content_excerpt': 'Valid excerpt',
                    'confidence_score': 0.8
                }
            ],
            processing_time=0.0,
            error=""
        )
        
        result = agent._validate_topics_node(state)
        
        assert len(result['topics']) == 1  # Only valid topic should remain
        assert result['topics'][0]['topic_name'] == 'Valid Topic'
    
    def test_validate_topics_node_with_error(self, agent):
        """Test validation when there's an error in state"""
        state = TopicExtractionState(
            text="Test text",
            max_topics=5,
            topics=[],
            processing_time=0.0,
            error="Previous error"
        )
        
        result = agent._validate_topics_node(state)
        
        assert result['error'] == "Previous error"  # Error should be preserved
    
    def test_extract_topics_integration(self, agent):
        """Test the main extract_topics method"""
        text = "Artificial intelligence and machine learning are key technologies."
        
        result = agent.extract_topics(text, max_topics=3)
        
        assert result['success'] is True
        assert result['total_topics'] == 2
        assert result['processing_time'] > 0
        assert result['error'] is None
    
    def test_extract_topics_with_empty_text(self, agent):
        """Test extraction with empty text"""
        result = agent.extract_topics("", max_topics=5)
        
        assert result['success'] is False
        assert "empty" in result['error'].lower()
    
    def test_extract_topics_with_invalid_max_topics(self, agent):
        """Test extraction with invalid max_topics"""
        result = agent.extract_topics("Test text", max_topics=0)
        
        assert result['success'] is False
        assert "max_topics" in result['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__]) 