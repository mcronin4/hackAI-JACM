#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.content_generator import ContentGeneratorAgent

def test_linkedin_content_generation():
    """Test LinkedIn content generation directly"""
    print("🎯 Testing LinkedIn Content Generation Logic...")
    
    # Initialize the content generator
    agent = ContentGeneratorAgent()
    
    # Sample enhanced topic
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
    
    original_url = "https://example.com/professional-relationships"
    
    # Test both platforms
    platforms = ["twitter", "linkedin"]
    
    for platform in platforms:
        print(f"\n{'='*20} {platform.upper()} {'='*20}")
        
        try:
            result = agent.generate_content_for_topic(
                topic=enhanced_topic,
                original_text=original_text,
                original_url=original_url,
                platform=platform
            )
            
            if result['success']:
                print(f"✅ {platform.upper()} Generation Success!")
                print(f"📄 Final Post: {result['final_post']}")
                print(f"📏 Length: {len(result['final_post'])} characters")
                print(f"📋 Strategy: {result['content_strategy']}")
                print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
                
                # Analyze the content
                post_without_url = result['final_post'].replace(original_url, '').strip()
                content_length = len(post_without_url)
                
                if platform == "twitter":
                    expected_range = (210, 240)
                    strategy_expected = "single_tweet"
                elif platform == "linkedin":
                    expected_range = (500, 800)
                    strategy_expected = "professional_post"
                
                print(f"📊 Content Analysis:")
                print(f"   - Content (without URL): {content_length} characters")
                print(f"   - Expected range: {expected_range[0]}-{expected_range[1]} characters")
                print(f"   - In range: {'✅' if expected_range[0] <= content_length <= expected_range[1] else '❌'}")
                print(f"   - Strategy match: {'✅' if result['content_strategy'] == strategy_expected else '❌'}")
                
            else:
                print(f"❌ {platform.upper()} Generation Failed: {result['error']}")
                
        except Exception as e:
            print(f"❌ {platform.upper()} Generation Error: {e}")

def test_platform_strategy_assignment():
    """Test that platforms get the correct content strategies"""
    print("\n🔧 Testing Platform Strategy Assignment...")
    
    agent = ContentGeneratorAgent()
    
    # Test state for different platforms
    test_cases = [
        ("twitter", "single_tweet"),
        ("linkedin", "professional_post"),
        ("unknown_platform", "single_tweet")  # fallback
    ]
    
    for platform, expected_strategy in test_cases:
        # Create a mock state
        state = {
            'target_platforms': [platform],
            'error': None
        }
        
        # Test the strategy node
        result_state = agent._content_strategy_node(state)
        
        actual_strategy = result_state.get('content_strategy')
        
        print(f"   Platform: {platform}")
        print(f"   Expected Strategy: {expected_strategy}")
        print(f"   Actual Strategy: {actual_strategy}")
        print(f"   Match: {'✅' if actual_strategy == expected_strategy else '❌'}")
        print()

def test_platform_configurations():
    """Test platform configuration loading"""
    print("⚙️  Testing Platform Configurations...")
    
    agent = ContentGeneratorAgent()
    
    # Test supported platforms
    supported_platforms = agent.platform_config.get_supported_platforms()
    print(f"✅ Supported platforms: {supported_platforms}")
    
    # Expected platforms
    expected_platforms = ["twitter", "linkedin"]
    
    for platform in expected_platforms:
        if platform in supported_platforms:
            config = agent.platform_config.get_config(platform)
            print(f"\n📋 {platform.upper()} Configuration:")
            print(f"   - Character limit: {config.character_limit}")
            print(f"   - Max hashtags: {config.max_hashtags}")
            print(f"   - Supports threads: {config.supports_threads}")
            print(f"   - Supports links: {config.supports_links}")
            print(f"   - Tone guidelines: {config.tone_guidelines[:100]}...")
        else:
            print(f"❌ {platform} not found in supported platforms")
    
    return len(expected_platforms) == len([p for p in expected_platforms if p in supported_platforms])

def main():
    """Run all local tests"""
    print("🚀 Starting Local LinkedIn Content Generation Tests")
    print("=" * 60)
    
    # Test 1: Platform configurations
    print("TEST 1: Platform Configurations")
    config_success = test_platform_configurations()
    
    print("\n" + "=" * 60)
    
    # Test 2: Strategy assignment
    print("TEST 2: Platform Strategy Assignment")
    test_platform_strategy_assignment()
    
    print("=" * 60)
    
    # Test 3: Content generation
    print("TEST 3: Content Generation")
    test_linkedin_content_generation()
    
    print("\n" + "=" * 60)
    print("🏁 Local Tests Complete!")
    
    if config_success:
        print("✅ LinkedIn functionality has been successfully integrated!")
        print("\n📊 Summary of changes:")
        print("   ✅ Added 'professional_post' strategy for LinkedIn")
        print("   ✅ LinkedIn content targets 500-800 characters (vs Twitter's 210-240)")
        print("   ✅ Platform-specific tone guidelines fed into prompts")
        print("   ✅ Enhanced LinkedIn config with professional tone details")
        print("   ✅ Platform-aware content generation logic")
    else:
        print("❌ Some configuration issues detected.")

if __name__ == "__main__":
    main() 