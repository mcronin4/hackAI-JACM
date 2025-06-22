import pytest
from unittest.mock import Mock, patch
from app.agents.content_generator import ContentGeneratorAgent, ContentGenerationState


class TestContentGeneratorAgent:
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        mock = Mock()
        # Default successful response for content generation
        mock.invoke.return_value.content = '''Generate engaging content about remote work productivity challenges. The struggle is real but there are solutions! What's your biggest WFH challenge?'''
        return mock
    
    @pytest.fixture
    def agent(self, mock_llm):
        """Create agent with mocked LLM"""
        with patch('app.agents.content_generator.ChatGoogleGenerativeAI', return_value=mock_llm):
            return ContentGeneratorAgent()
    
    @pytest.fixture
    def sample_topic(self):
        """Sample enhanced topic for testing"""
        return {
            "topic_id": 1,
            "topic_name": "Remote Work Productivity Challenges",
            "content_excerpt": "Many professionals struggle with distractions when working from home, leading to decreased productivity and increased stress.",
            "primary_emotion": "Justify Their Failures",
            "emotion_confidence": 0.85,
            "reasoning": "This topic validates the common struggle with remote work productivity, allowing the audience to feel understood rather than blamed for their challenges."
        }
    
    @pytest.fixture
    def sample_state(self, sample_topic):
        """Sample state for testing"""
        return ContentGenerationState(
            original_text="Full article about remote work challenges and solutions...",
            topics=[sample_topic],
            target_platforms=["twitter"],
            original_url="https://example.com/remote-work-article",
            current_topic=sample_topic,
            content_strategy="single_tweet",
            generated_content="",
            hashtags=[],
            call_to_action="",
            final_post="",
            processing_time=0.0,
            error=""
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert agent.graph is not None
        assert agent.platform_config is not None
    
    def test_input_processing_node(self, agent, sample_state):
        """Test input processing node"""
        result = agent._input_processing_node(sample_state)
        
        assert result['error'] == ""
        assert result['current_topic'] == sample_state['topics'][0]
        assert result['target_platforms'] == ["twitter"]
    
    def test_content_strategy_node(self, agent, sample_state):
        """Test content strategy node returns single_tweet for now"""
        result = agent._content_strategy_node(sample_state)
        
        assert result['content_strategy'] == "single_tweet"
        assert result['error'] == ""
    
    def test_content_generation_node_success(self, agent, sample_state):
        """Test successful content generation"""
        result = agent._content_generation_node(sample_state)
        
        assert result['generated_content'] != ""
        assert len(result['generated_content']) <= 200  # Leave room for hashtags and CTA
        assert result['error'] == ""
    
    def test_hashtag_generation_node_success(self, agent, sample_state):
        """Test successful hashtag generation"""
        # Mock hashtag response
        agent.llm.invoke.return_value.content = "#RemoteWork #Productivity #WorkFromHome"
        
        result = agent._hashtag_generation_node(sample_state)
        
        assert len(result['hashtags']) <= 3
        assert all(tag.startswith('#') for tag in result['hashtags'])
        assert result['error'] == ""
    
    def test_hashtag_generation_node_failure_graceful(self, agent, sample_state):
        """Test hashtag generation failure doesn't break the flow"""
        # Mock hashtag failure
        agent.llm.invoke.side_effect = Exception("Hashtag generation failed")
        
        result = agent._hashtag_generation_node(sample_state)
        
        assert result['hashtags'] == []  # Should return empty list, not fail
        assert result['error'] == ""  # Should not propagate error
    
    def test_cta_generation_node_success(self, agent, sample_state):
        """Test successful CTA generation"""
        # Mock CTA response
        agent.llm.invoke.return_value.content = "What's your biggest WFH challenge? Full breakdown:"
        
        result = agent._cta_generation_node(sample_state)
        
        assert result['call_to_action'] != ""
        assert result['error'] == ""
    
    def test_validation_node_success(self, agent, sample_state):
        """Test validation node with valid content"""
        # Set up state with content
        sample_state['generated_content'] = "Great content about remote work"
        sample_state['hashtags'] = ["#RemoteWork", "#Productivity"]
        sample_state['call_to_action'] = "Read more:"
        
        result = agent._validation_node(sample_state)
        
        assert result['error'] == ""
    
    def test_validation_node_too_long(self, agent, sample_state):
        """Test validation node catches content that's too long"""
        # Set up state with content that's too long
        sample_state['generated_content'] = "A" * 250
        sample_state['hashtags'] = ["#RemoteWork", "#Productivity", "#WorkFromHome"]
        sample_state['call_to_action'] = "Read the full article:"
        
        result = agent._validation_node(sample_state)
        
        assert "character limit" in result['error'].lower()
    
    def test_formatting_node(self, agent, sample_state):
        """Test formatting node combines all elements correctly"""
        # Set up state with all components
        sample_state['generated_content'] = "Remote work challenges are real but solvable"
        sample_state['hashtags'] = ["#RemoteWork", "#Productivity"]
        sample_state['call_to_action'] = "What's your experience?"
        sample_state['original_url'] = "https://example.com/article"
        
        result = agent._formatting_node(sample_state)
        
        final_post = result['final_post']
        assert sample_state['generated_content'] in final_post
        assert "#RemoteWork" in final_post
        assert "#Productivity" in final_post
        assert sample_state['call_to_action'] in final_post
        assert sample_state['original_url'] in final_post
    
    def test_generate_content_for_topic_success(self, agent, sample_topic):
        """Test the main method for generating content for a single topic"""
        original_text = "Full article about remote work..."
        original_url = "https://example.com/article"
        
        result = agent.generate_content_for_topic(
            topic=sample_topic,
            original_text=original_text,
            original_url=original_url,
            platform="twitter"
        )
        
        assert result['success'] is True
        assert result['final_post'] != ""
        assert result['processing_time'] > 0
        assert result['error'] is None
    
    def test_generate_content_for_topic_with_error(self, agent, sample_topic):
        """Test error handling in main method"""
        # Mock LLM to raise an exception
        agent.llm.invoke.side_effect = Exception("LLM failed")
        
        result = agent.generate_content_for_topic(
            topic=sample_topic,
            original_text="Test text",
            original_url="https://example.com/test",
            platform="twitter"
        )
        
        assert result['success'] is False
        assert result['error'] is not None
        assert result['final_post'] == ""
    
    def test_unsupported_platform(self, agent, sample_topic):
        """Test handling of unsupported platforms"""
        result = agent.generate_content_for_topic(
            topic=sample_topic,
            original_text="Test text",
            original_url="https://example.com/test",
            platform="unsupported_platform"
        )
        
        assert result['success'] is False
        assert "unsupported platform" in result['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__]) 