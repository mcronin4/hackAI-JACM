import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.content_pipeline import ContentPipelineService, ContentPipelineError
from app.models import Topic, EnhancedTopic, GeneratedContent
import asyncio


class TestContentPipelineService:
    """Test suite for the unified content pipeline service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ContentPipelineService()
        
        # Mock data
        self.sample_text = "Artificial intelligence is revolutionizing the way we work and live."
        self.sample_url = "https://example.com/ai-article"
        
        self.mock_topics = [
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
        ]
        
        self.mock_enhanced_topics = [
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
        ]
        
        self.mock_generated_content = [
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

    @pytest.mark.asyncio
    async def test_process_content_success_full_flow(self):
        """Test successful processing through all three agents"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock topic extraction
            mock_topic_extract.return_value = {
                'success': True,
                'topics': self.mock_topics,
                'total_topics': 2,
                'processing_time': 0.5
            }
            
            # Mock emotion analysis
            mock_emotion_analyze.return_value = {
                'success': True,
                'emotion_analysis': self.mock_enhanced_topics,
                'total_analyzed': 2,
                'processing_time': 0.8
            }
            
            # Mock content generation (called twice, once per topic)
            mock_content_gen.side_effect = [
                self.mock_generated_content[0],
                self.mock_generated_content[1]
            ]
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url,
                max_topics=5,
                target_platforms=['twitter']
            )
            
            # Verify the result
            assert result['success'] is True
            assert len(result['generated_posts']) == 2
            assert result['total_topics'] == 2
            assert result['successful_generations'] == 2
            assert result['processing_time'] > 0
            
            # Verify the generated posts
            posts = result['generated_posts']
            assert posts[0] == self.mock_generated_content[0]['final_post']
            assert posts[1] == self.mock_generated_content[1]['final_post']
            
            # Verify agent calls
            mock_topic_extract.assert_called_once_with(self.sample_text, 5)
            mock_emotion_analyze.assert_called_once()
            assert mock_content_gen.call_count == 2

    @pytest.mark.asyncio
    async def test_process_content_topic_extraction_failure(self):
        """Test handling of topic extraction failure"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract:
            
            # Mock topic extraction failure
            mock_topic_extract.return_value = {
                'success': False,
                'error': 'Failed to parse topics from LLM response',
                'topics': [],
                'total_topics': 0,
                'processing_time': 0.5
            }
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify failure handling
            assert result['success'] is False
            assert 'Failed to parse topics' in result['error']
            assert result['generated_posts'] == []
            assert result['total_topics'] == 0

    @pytest.mark.asyncio
    async def test_process_content_emotion_analysis_failure(self):
        """Test handling of emotion analysis failure"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze:
            
            # Mock successful topic extraction
            mock_topic_extract.return_value = {
                'success': True,
                'topics': self.mock_topics,
                'total_topics': 2,
                'processing_time': 0.5
            }
            
            # Mock emotion analysis failure
            mock_emotion_analyze.return_value = {
                'success': False,
                'error': 'LLM API error during emotion analysis',
                'emotion_analysis': [],
                'total_analyzed': 0,
                'processing_time': 0.8
            }
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify failure handling
            assert result['success'] is False
            assert 'emotion analysis' in result['error']
            assert result['generated_posts'] == []

    @pytest.mark.asyncio
    async def test_process_content_generation_partial_failure(self):
        """Test handling when some content generation fails"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock successful topic extraction and emotion analysis
            mock_topic_extract.return_value = {
                'success': True,
                'topics': self.mock_topics,
                'total_topics': 2,
                'processing_time': 0.5
            }
            
            mock_emotion_analyze.return_value = {
                'success': True,
                'emotion_analysis': self.mock_enhanced_topics,
                'total_analyzed': 2,
                'processing_time': 0.8
            }
            
            # Mock partial content generation failure
            mock_content_gen.side_effect = [
                self.mock_generated_content[0],  # First succeeds
                {  # Second fails
                    'topic_id': 2,
                    'platform': 'twitter',
                    'final_post': '',
                    'content_strategy': '',
                    'hashtags': [],
                    'call_to_action': '',
                    'success': False,
                    'error': 'Content generation timeout',
                    'processing_time': 0.1
                }
            ]
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify failure handling (entire flow should fail)
            assert result['success'] is False
            assert 'Content generation failed for some topics' in result['error']
            assert result['generated_posts'] == []

    @pytest.mark.asyncio
    async def test_process_content_invalid_input(self):
        """Test handling of invalid input parameters"""
        
        # Test empty text
        result = await self.service.process_content(
            text="",
            original_url=self.sample_url
        )
        assert result['success'] is False
        assert 'empty' in result['error'].lower()
        
        # Test empty URL
        result = await self.service.process_content(
            text=self.sample_text,
            original_url=""
        )
        assert result['success'] is False
        assert 'url' in result['error'].lower()
        
        # Test invalid max_topics
        result = await self.service.process_content(
            text=self.sample_text,
            original_url=self.sample_url,
            max_topics=0
        )
        assert result['success'] is False
        assert 'max_topics' in result['error'].lower()

    @pytest.mark.asyncio
    async def test_process_content_default_parameters(self):
        """Test that default parameters are applied correctly"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock successful responses
            mock_topic_extract.return_value = {'success': True, 'topics': [], 'total_topics': 0, 'processing_time': 0.1}
            mock_emotion_analyze.return_value = {'success': True, 'emotion_analysis': [], 'total_analyzed': 0, 'processing_time': 0.1}
            
            # Execute with minimal parameters
            await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify default parameters were used
            mock_topic_extract.assert_called_once_with(self.sample_text, 10)  # Default max_topics

    def test_service_initialization(self):
        """Test that the service initializes all agents correctly"""
        service = ContentPipelineService()
        
        assert service.topic_extractor is not None
        assert service.emotion_analyzer is not None
        assert service.content_generator is not None
        assert hasattr(service.topic_extractor, 'extract_topics')
        assert hasattr(service.emotion_analyzer, 'analyze_emotions')
        assert hasattr(service.content_generator, 'generate_content_for_topic')

    @pytest.mark.asyncio
    async def test_process_content_multiple_platforms(self):
        """Test processing content for multiple platforms"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock responses
            mock_topic_extract.return_value = {
                'success': True,
                'topics': [self.mock_topics[0]],  # Just one topic
                'total_topics': 1,
                'processing_time': 0.5
            }
            
            mock_emotion_analyze.return_value = {
                'success': True,
                'emotion_analysis': [self.mock_enhanced_topics[0]],
                'total_analyzed': 1,
                'processing_time': 0.8
            }
            
            # Mock content generation for multiple platforms
            mock_content_gen.side_effect = [
                {**self.mock_generated_content[0], 'platform': 'twitter'},
                {**self.mock_generated_content[0], 'platform': 'linkedin', 'final_post': 'LinkedIn version of the post'}
            ]
            
            # Execute with multiple platforms
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url,
                target_platforms=['twitter', 'linkedin']
            )
            
            # Verify multiple posts generated
            assert result['success'] is True
            assert len(result['generated_posts']) == 2
            assert mock_content_gen.call_count == 2 