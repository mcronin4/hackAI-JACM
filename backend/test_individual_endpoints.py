#!/usr/bin/env python3

import requests
import json
import time

def test_topic_extraction():
    """Test the topic extraction endpoint"""
    print("🔍 Testing Topic Extraction Endpoint...")
    
    test_request = {
        "text": "Artificial intelligence is revolutionizing healthcare by enabling early disease detection through machine learning algorithms that analyze medical images with unprecedented accuracy. These AI systems can identify patterns in X-rays, MRIs, and CT scans that human doctors might miss, leading to faster diagnosis and treatment. Additionally, AI-powered drug discovery platforms are accelerating the development of new medications by predicting molecular interactions and identifying promising compounds years faster than traditional methods."
    }
    
    url = "http://localhost:8000/api/v1/extract-topics"
    
    try:
        response = requests.post(url, json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Topic Extraction Success!")
            print(f"   - Extracted {result['total_topics']} topics")
            print(f"   - Processing time: {result['processing_time']:.2f}s")
            
            for i, topic in enumerate(result['topics'], 1):
                print(f"   Topic {i}: {topic['topic_name']}")
                print(f"   Confidence: {topic['confidence_score']:.2f}")
                print(f"   Excerpt: {topic['content_excerpt'][:100]}...")
                print()
            
            return result['topics']
        else:
            print(f"❌ Topic Extraction Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Topic Extraction Error: {e}")
        return None


def test_emotion_analysis(topics):
    """Test the emotion analysis endpoint"""
    if not topics:
        print("⏭️  Skipping Emotion Analysis - No topics available")
        return None
        
    print("🎭 Testing Emotion Analysis Endpoint...")
    
    test_request = {
        "topics": topics
    }
    
    url = "http://localhost:8000/api/v1/analyze-emotions"
    
    try:
        response = requests.post(url, json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Emotion Analysis Success!")
            print(f"   - Analyzed {result['total_topics']} topics")
            print(f"   - Processing time: {result['processing_time']:.2f}s")
            
            for topic in result['enhanced_topics']:
                print(f"   Topic {topic['topic_id']}: {topic['topic_name']}")
                print(f"   Primary Emotion: {topic['primary_emotion']} (confidence: {topic['emotion_confidence']:.2f})")
                print(f"   Emotion Description: {topic['emotion_description']}")
                print(f"   Reasoning: {topic['reasoning'][:100]}...")
                print()
            
            return result['enhanced_topics']
        else:
            print(f"❌ Emotion Analysis Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Emotion Analysis Error: {e}")
        return None


def test_content_generation(enhanced_topics):
    """Test the content generation endpoint"""
    if not enhanced_topics:
        print("⏭️  Skipping Content Generation - No enhanced topics available")
        return None
        
    print("📝 Testing Content Generation Endpoint...")
    
    test_request = {
        "original_text": "Artificial intelligence is revolutionizing healthcare by enabling early disease detection through machine learning algorithms that analyze medical images with unprecedented accuracy. These AI systems can identify patterns in X-rays, MRIs, and CT scans that human doctors might miss, leading to faster diagnosis and treatment. Additionally, AI-powered drug discovery platforms are accelerating the development of new medications by predicting molecular interactions and identifying promising compounds years faster than traditional methods.",
        "topics": enhanced_topics,
        "original_url": "https://example.com/ai-healthcare-article",
        "target_platforms": ["twitter"]
    }
    
    url = "http://localhost:8000/api/v1/generate-content"
    
    try:
        response = requests.post(url, json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Content Generation Success!")
            print(f"   - Generated {result['total_generated']} content pieces")
            print(f"   - Successful: {result['successful_generations']}")
            print(f"   - Processing time: {result['processing_time']:.2f}s")
            
            for content in result['generated_content']:
                if content['success']:
                    print(f"   📱 Platform: {content['platform']}")
                    print(f"   📄 Post: {content['final_post']}")
                    print(f"   📋 Strategy: {content['content_strategy']}")
                    print(f"   📢 CTA: {content['call_to_action']}")
                    print()
                else:
                    print(f"   ❌ Failed for topic {content['topic_id']}: {content['error']}")
            
            return result['generated_content']
        else:
            print(f"❌ Content Generation Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Content Generation Error: {e}")
        return None


def test_unified_pipeline():
    """Test the unified pipeline endpoint"""
    print("🔄 Testing Unified Pipeline Endpoint...")
    
    test_request = {
        "text": "Artificial intelligence is revolutionizing healthcare by enabling early disease detection through machine learning algorithms that analyze medical images with unprecedented accuracy. These AI systems can identify patterns in X-rays, MRIs, and CT scans that human doctors might miss, leading to faster diagnosis and treatment. Additionally, AI-powered drug discovery platforms are accelerating the development of new medications by predicting molecular interactions and identifying promising compounds years faster than traditional methods.",
        "original_url": "https://example.com/ai-healthcare-article",
        "target_platforms": ["twitter"]
    }
    
    url = "http://localhost:8000/api/v1/generate-posts"
    
    try:
        response = requests.post(url, json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Unified Pipeline Success!")
            print(f"   - Generated {len(result['generated_posts'])} posts")
            print(f"   - Total topics: {result['total_topics']}")
            print(f"   - Successful generations: {result['successful_generations']}")
            print(f"   - Processing time: {result['processing_time']:.2f}s")
            
            for i, post in enumerate(result['generated_posts'], 1):
                print(f"   Post {i}: {post}")
                print()
            
            return result
        else:
            print(f"❌ Unified Pipeline Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Unified Pipeline Error: {e}")
        return None


def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check Endpoint...")
    
    url = "http://localhost:8000/api/v1/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health Check Success!")
            print(f"   - Service Status: {result['status']}")
            
            for agent_name, agent_info in result['agents'].items():
                print(f"   - {agent_name}: {agent_info['status']}")
                if 'model' in agent_info:
                    print(f"     Model: {agent_info['model']}")
                if 'temperature' in agent_info:
                    print(f"     Temperature: {agent_info['temperature']}")
            
            return result
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return None


def main():
    print("🚀 Testing Individual Agent Endpoints")
    print("=" * 60)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test health check first
    health_result = test_health_check()
    print()
    
    if not health_result or health_result.get('status') != 'healthy':
        print("❌ Server is not healthy. Stopping tests.")
        return
    
    # Test individual endpoints in sequence
    print("Testing Individual Endpoints:")
    print("-" * 40)
    
    # 1. Topic Extraction
    topics = test_topic_extraction()
    print()
    
    # 2. Emotion Analysis
    enhanced_topics = test_emotion_analysis(topics)
    print()
    
    # 3. Content Generation
    generated_content = test_content_generation(enhanced_topics)
    print()
    
    # 4. Unified Pipeline
    print("Testing Unified Pipeline:")
    print("-" * 40)
    pipeline_result = test_unified_pipeline()
    print()
    
    # Summary
    print("=" * 60)
    print("🏁 Test Summary:")
    print(f"   - Topic Extraction: {'✅ Pass' if topics else '❌ Fail'}")
    print(f"   - Emotion Analysis: {'✅ Pass' if enhanced_topics else '❌ Fail'}")
    print(f"   - Content Generation: {'✅ Pass' if generated_content else '❌ Fail'}")
    print(f"   - Unified Pipeline: {'✅ Pass' if pipeline_result else '❌ Fail'}")
    print(f"   - Health Check: {'✅ Pass' if health_result else '❌ Fail'}")


if __name__ == "__main__":
    main() 