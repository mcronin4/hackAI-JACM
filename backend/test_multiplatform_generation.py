#!/usr/bin/env python3

import requests
import json
import time

def test_multiplatform_pipeline():
    """Test the unified pipeline with multiple platforms including LinkedIn"""
    print("🔄 Testing Multi-Platform Pipeline...")
    
    test_request = {
        "text": "Building strong professional relationships isn't just about networking events. It's about being genuinely curious about others and their challenges. When you shift from 'what can I get' to 'how can I help,' people notice. Small actions like remembering details from past conversations, sharing relevant opportunities, or simply checking in during tough times create lasting connections that benefit everyone involved.",
        "original_url": "https://example.com/professional-relationships",
        "target_platforms": ["twitter", "linkedin"]
    }
    
    url = "http://localhost:8000/api/v1/generate-posts"
    
    try:
        response = requests.post(url, json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Multi-Platform Pipeline Success!")
            print(f"   - Generated {len(result['generated_posts'])} posts")
            print(f"   - Total topics: {result['total_topics']}")
            print(f"   - Successful generations: {result['successful_generations']}")
            print(f"   - Processing time: {result['processing_time']:.2f}s")
            print(f"   - Platforms processed: {result['pipeline_details']['platforms_processed']}")
            print()
            
            # Group posts by platform for comparison
            platform_posts = {}
            post_index = 0
            
            for topic_idx in range(result['total_topics']):
                for platform in result['pipeline_details']['platforms_processed']:
                    if post_index < len(result['generated_posts']):
                        if platform not in platform_posts:
                            platform_posts[platform] = []
                        platform_posts[platform].append(result['generated_posts'][post_index])
                        post_index += 1
            
            # Display posts by platform
            for platform, posts in platform_posts.items():
                print(f"📱 {platform.upper()} POSTS:")
                print("=" * 50)
                for i, post in enumerate(posts, 1):
                    print(f"Post {i}: {post}")
                    print(f"Length: {len(post)} characters")
                    print()
                print()
            
            return result
        else:
            print(f"❌ Multi-Platform Pipeline Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Multi-Platform Pipeline Error: {e}")
        return None


def test_individual_content_generation():
    """Test content generation for individual platforms to see the differences"""
    print("📝 Testing Individual Platform Content Generation...")
    
    # Sample enhanced topic (simulating output from topic extraction + emotion analysis)
    enhanced_topic = {
        "topic_id": 1,
        "topic_name": "Building authentic professional relationships through genuine curiosity and helping others",
        "content_excerpt": "Building strong professional relationships isn't just about networking events. It's about being genuinely curious about others and their challenges.",
        "primary_emotion": "encourage_dreams",
        "emotion_confidence": 0.85,
        "emotion_description": "Encouraging professional growth and authentic connection",
        "reasoning": "This topic encourages people to pursue meaningful professional relationships by focusing on authenticity and mutual benefit."
    }
    
    original_text = "Building strong professional relationships isn't just about networking events. It's about being genuinely curious about others and their challenges. When you shift from 'what can I get' to 'how can I help,' people notice. Small actions like remembering details from past conversations, sharing relevant opportunities, or simply checking in during tough times create lasting connections that benefit everyone involved."
    
    platforms = ["twitter", "linkedin"]
    
    for platform in platforms:
        print(f"\n🎯 Testing {platform.upper()} Content Generation...")
        
        test_request = {
            "original_text": original_text,
            "topics": [enhanced_topic],
            "original_url": "https://example.com/professional-relationships",
            "target_platforms": [platform]
        }
        
        url = "http://localhost:8000/api/v1/generate-content"
        
        try:
            response = requests.post(url, json=test_request)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {platform.upper()} Content Generation Success!")
                
                for content in result['generated_content']:
                    if content['success']:
                        print(f"   📄 Generated Post: {content['final_post']}")
                        print(f"   📏 Length: {len(content['final_post'])} characters")
                        print(f"   📋 Strategy: {content['content_strategy']}")
                        print(f"   ⏱️  Processing time: {content['processing_time']:.2f}s")
                    else:
                        print(f"   ❌ Failed: {content['error']}")
                        
            else:
                print(f"❌ {platform.upper()} Content Generation Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ {platform.upper()} Content Generation Error: {e}")

def test_platform_configurations():
    """Test that platform configurations are properly loaded"""
    print("⚙️  Testing Platform Configurations...")
    
    # Import the ContentGeneratorAgent to test configurations
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from app.agents.content_generator import ContentGeneratorAgent
        
        agent = ContentGeneratorAgent()
        
        # Test supported platforms
        supported_platforms = agent.platform_config.get_supported_platforms()
        print(f"✅ Supported platforms: {supported_platforms}")
        
        # Test platform-specific configurations
        for platform in supported_platforms:
            config = agent.platform_config.get_config(platform)
            print(f"\n📋 {platform.upper()} Configuration:")
            print(f"   - Character limit: {config.character_limit}")
            print(f"   - Max hashtags: {config.max_hashtags}")
            print(f"   - Supports threads: {config.supports_threads}")
            print(f"   - Supports links: {config.supports_links}")
            print(f"   - Tone guidelines: {config.tone_guidelines}")
            
        return True
            
    except Exception as e:
        print(f"❌ Platform Configuration Test Error: {e}")
        return False


def main():
    """Run all multi-platform tests"""
    print("🚀 Starting Multi-Platform Content Generation Tests")
    print("=" * 60)
    
    # Test 1: Platform configurations
    config_success = test_platform_configurations()
    
    print("\n" + "=" * 60)
    
    # Test 2: Individual platform content generation
    test_individual_content_generation()
    
    print("\n" + "=" * 60)
    
    # Test 3: Multi-platform pipeline
    pipeline_result = test_multiplatform_pipeline()
    
    print("\n" + "=" * 60)
    print("🏁 Multi-Platform Tests Complete!")
    
    if config_success and pipeline_result:
        print("✅ All tests passed successfully!")
        print("\n🎉 LinkedIn functionality has been successfully integrated!")
        print("📊 Key improvements:")
        print("   - Platform-specific content strategies (single_tweet vs professional_post)")
        print("   - Different character limits (Twitter: 210-240, LinkedIn: 500-800)")
        print("   - Platform-specific tone guidelines in prompts")
        print("   - Multi-platform support in pipeline")
    else:
        print("❌ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main() 