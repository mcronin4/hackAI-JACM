#!/usr/bin/env python3
"""
Manual test script for the unified content pipeline.
This script tests the pipeline without pytest dependencies.
"""

import asyncio
import sys
import os
from unittest.mock import Mock, patch
import json

# Add the current directory to the path
sys.path.insert(0, os.path.abspath('.'))

def test_pipeline_models():
    """Test that our new models work correctly"""
    print("🧪 Testing Pipeline Models...")
    
    try:
        from app.models import ContentPipelineRequest, ContentPipelineResponse
        
        # Test request model
        request = ContentPipelineRequest(
            text="Test article about AI and the future of work.",
            original_url="https://example.com/test-article",
            max_topics=3,
            target_platforms=["twitter"]
        )
        
        print(f"✅ Request model created: {request.text[:50]}...")
        
        # Test response model
        response = ContentPipelineResponse(
            success=True,
            generated_posts=["Post 1", "Post 2"],
            total_topics=2,
            successful_generations=2,
            processing_time=1.5
        )
        
        print(f"✅ Response model created: {len(response.generated_posts)} posts")
        print("✅ Pipeline models work correctly!")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False
    
    return True

def test_pipeline_service_mock():
    """Test the pipeline service with mocked agents"""
    print("\n🧪 Testing Pipeline Service (with mocked agents)...")
    
    try:
        # Mock the agent classes before importing
        with patch('app.agents.topic_extractor.TopicExtractorAgent') as mock_topic, \
             patch('app.agents.emotion_targeting.EmotionTargetingAgent') as mock_emotion, \
             patch('app.agents.content_generator.ContentGeneratorAgent') as mock_content:
            
            # Configure mocks
            mock_topic_instance = Mock()
            mock_emotion_instance = Mock()
            mock_content_instance = Mock()
            
            mock_topic.return_value = mock_topic_instance
            mock_emotion.return_value = mock_emotion_instance
            mock_content.return_value = mock_content_instance
            
            # Mock the agent responses
            mock_topic_instance.extract_topics.return_value = {
                'success': True,
                'topics': [
                    {
                        'topic_id': 1,
                        'topic_name': 'Artificial Intelligence',
                        'content_excerpt': 'AI is revolutionizing how we work',
                        'confidence_score': 0.9
                    }
                ],
                'total_topics': 1,
                'processing_time': 0.5
            }
            
            mock_emotion_instance.analyze_emotions.return_value = {
                'success': True,
                'emotion_analysis': [
                    {
                        'topic_id': 1,
                        'topic_name': 'Artificial Intelligence',
                        'content_excerpt': 'AI is revolutionizing how we work',
                        'primary_emotion': 'encourage_dreams',
                        'emotion_confidence': 0.85,
                        'reasoning': 'This topic inspires future possibilities'
                    }
                ],
                'total_analyzed': 1,
                'processing_time': 0.8
            }
            
            mock_content_instance.generate_content_for_topic.return_value = {
                'success': True,
                'final_post': 'AI is transforming our world! 🚀 Discover how artificial intelligence is creating new opportunities for growth and innovation. Ready to embrace the future? https://example.com/test',
                'content_strategy': 'single_tweet',
                'hashtags': [],
                'call_to_action': 'Ready to embrace the future?',
                'processing_time': 1.2
            }
            
            # Now import and test the service
            from app.services.content_pipeline import ContentPipelineService
            
            async def run_test():
                service = ContentPipelineService()
                
                result = await service.process_content(
                    text="Artificial intelligence is revolutionizing how we work and live.",
                    original_url="https://example.com/test-article",
                    max_topics=3,
                    target_platforms=["twitter"]
                )
                
                return result
            
            # Run the async test
            result = asyncio.run(run_test())
            
            print(f"✅ Pipeline processed successfully: {result['success']}")
            print(f"✅ Generated {len(result['generated_posts'])} posts")
            print(f"✅ Processing time: {result['processing_time']:.2f}s")
            
            if result['generated_posts']:
                print(f"✅ Sample post: {result['generated_posts'][0][:100]}...")
            
            print("✅ Pipeline service works correctly!")
            
    except Exception as e:
        print(f"❌ Pipeline service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_api_routes_import():
    """Test that API routes can be imported"""
    print("\n🧪 Testing API Routes Import...")
    
    try:
        # Mock the service before importing routes
        with patch('app.services.content_pipeline.ContentPipelineService'):
            from app.api.routes import router
            
            print(f"✅ Router imported successfully")
            print(f"✅ Router prefix: {router.prefix}")
            print(f"✅ Router tags: {router.tags}")
            print("✅ API routes work correctly!")
            
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
        return False
    
    return True

def main():
    """Run all manual tests"""
    print("🚀 Starting Manual Pipeline Tests...")
    print("=" * 50)
    
    tests = [
        test_pipeline_models,
        test_pipeline_service_mock,
        test_api_routes_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your pipeline is ready!")
        print("\nNext steps:")
        print("1. Set up your environment variables (GOOGLE_API_KEY, etc.)")
        print("2. Start the FastAPI server: uvicorn main:app --reload")
        print("3. Test the API at http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 