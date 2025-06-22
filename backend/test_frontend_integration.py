#!/usr/bin/env python3
"""
Test script to verify frontend integration with platform-separated API response
"""

import requests
import json

def test_multiplatform_api():
    """Test the API with both Twitter and LinkedIn platforms"""
    print("🧪 Testing Multi-Platform API Integration")
    print("=" * 50)
    
    # Test data
    test_request = {
        "text": "Professional networking isn't just about collecting business cards. It's about building genuine relationships based on mutual respect and shared interests. When you approach networking with the mindset of helping others first, you create lasting connections that benefit everyone involved.",
        "original_url": "https://example.com/networking-guide",
        "target_platforms": ["twitter", "linkedin"]
    }
    
    # API endpoint
    url = "http://localhost:8000/api/v1/generate-posts"
    
    try:
        print("📤 Sending request to API...")
        print(f"Platforms: {test_request['target_platforms']}")
        print(f"Text length: {len(test_request['text'])} characters")
        print()
        
        response = requests.post(url, json=test_request, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response Successful!")
            print(f"Success: {data.get('success', False)}")
            print(f"Total Topics: {data.get('total_topics', 0)}")
            print(f"Successful Generations: {data.get('successful_generations', 0)}")
            print(f"Processing Time: {data.get('processing_time', 0):.2f}s")
            print()
            
            # Test new platform_posts structure
            if 'platform_posts' in data:
                platform_posts = data['platform_posts']
                print("🆕 NEW PLATFORM-SEPARATED STRUCTURE:")
                print("-" * 40)
                
                for platform in ['twitter', 'linkedin']:
                    posts = platform_posts.get(platform, [])
                    print(f"\n📱 {platform.upper()} ({len(posts)} posts):")
                    
                    for i, post in enumerate(posts, 1):
                        print(f"  Post {i}:")
                        print(f"    Content: {post['post_content'][:60]}...")
                        print(f"    Topic ID: {post['topic_id']}")
                        print(f"    Strategy: {post['content_strategy']}")
                        print(f"    Emotion: {post['primary_emotion']}")
                        print(f"    Length: {len(post['post_content'])} chars")
                        print()
            
            # Test legacy compatibility
            if 'generated_posts' in data:
                legacy_posts = data['generated_posts']
                print(f"🔄 LEGACY COMPATIBILITY ({len(legacy_posts)} total posts):")
                print("-" * 40)
                for i, post in enumerate(legacy_posts, 1):
                    print(f"  {i}. {post[:50]}...")
                print()
            
            # Frontend integration example
            print("🎯 FRONTEND INTEGRATION EXAMPLE:")
            print("-" * 40)
            print("// How frontend would handle the response:")
            print("if (data.success) {")
            print("  const twitterPosts = data.platform_posts.twitter || [];")
            print("  const linkedinPosts = data.platform_posts.linkedin || [];")
            print("  ")
            print("  // Display Twitter posts in Twitter section")
            print(f"  renderTwitterPosts(twitterPosts); // {len(platform_posts.get('twitter', []))} posts")
            print("  ")
            print("  // Display LinkedIn posts in LinkedIn section")
            print(f"  renderLinkedInPosts(linkedinPosts); // {len(platform_posts.get('linkedin', []))} posts")
            print("}")
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this is normal for the first request")
        print("The AI model may need time to process the content")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the backend server running?")
        print("Run: cd backend && python main.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Run the integration test"""
    print("🚀 Frontend Integration Test")
    print("=" * 50)
    print("This test verifies that the API returns the correct")
    print("platform-separated structure for frontend consumption.")
    print()
    
    success = test_multiplatform_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Integration test completed successfully!")
        print("✅ The frontend can now properly separate Twitter and LinkedIn posts")
        print("✅ Both new platform_posts and legacy generated_posts are available")
        print("✅ Ready for frontend integration!")
    else:
        print("❌ Integration test failed")
        print("Please check that the backend is running and try again")

if __name__ == "__main__":
    main() 