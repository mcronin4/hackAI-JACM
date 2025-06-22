#!/usr/bin/env python3
"""
Test script for the streaming posts API endpoint.
This demonstrates how the streaming functionality works.
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_streaming_posts():
    """Test the streaming posts API endpoint"""
    print("🧪 Testing /api/v1/stream-posts endpoint...")
    
    # Test data
    test_data = {
        "text": "Artificial intelligence is revolutionizing the way we work and live. From automated customer service to predictive analytics, AI is helping businesses become more efficient and effective. However, with great power comes great responsibility, and we must ensure that AI development is ethical and transparent.",
        "target_platforms": ["twitter", "linkedin"]
    }
    
    try:
        print(f"📤 Sending streaming request to: {API_URL}/api/v1/stream-posts")
        print(f"📝 Request data: {json.dumps(test_data, indent=2)}")
        
        # Make streaming request
        response = requests.post(
            f"{API_URL}/api/v1/stream-posts",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            },
            stream=True,  # Enable streaming
            timeout=60
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n🎉 Streaming response received! Processing events...\n")
            
            posts_received = 0
            buffer = ""
            
            # Process streaming response
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    lines = buffer.split('\n')
                    buffer = lines.pop()  # Keep incomplete line in buffer
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        if line.startswith('event: '):
                            event_type = line[7:]  # Remove 'event: '
                            print(f"📡 Event Type: {event_type}")
                        
                        elif line.startswith('data: '):
                            try:
                                data_json = line[6:]  # Remove 'data: '
                                event_data = json.loads(data_json)
                                
                                # Handle different event types
                                if 'post_content' in event_data:
                                    posts_received += 1
                                    print(f"\n✅ Post #{posts_received} received:")
                                    print(f"   Platform: {event_data.get('platform', 'unknown')}")
                                    print(f"   Topic: {event_data.get('topic_name', 'N/A')}")
                                    print(f"   Strategy: {event_data.get('content_strategy', 'N/A')}")
                                    print(f"   Processing Time: {event_data.get('processing_time', 0):.2f}s")
                                    print(f"   Content Preview: {event_data.get('post_content', '')[:100]}...")
                                    
                                    if 'progress' in event_data:
                                        progress = event_data['progress']
                                        print(f"   Progress: {progress['completed']}/{progress['total']}")
                                
                                elif 'message' in event_data:
                                    print(f"ℹ️  Status: {event_data['message']}")
                                    if 'stage' in event_data:
                                        print(f"   Stage: {event_data['stage']}")
                                
                                elif 'error' in event_data:
                                    print(f"❌ Error: {event_data['error']}")
                                
                                elif event_data.get('event') == 'complete':
                                    print(f"\n🎊 Generation Complete!")
                                    print(f"   Total Processing Time: {event_data.get('total_processing_time', 0):.2f}s")
                                    break
                                    
                            except json.JSONDecodeError as e:
                                print(f"⚠️  JSON decode error: {e}")
                                print(f"   Raw data: {data_json[:100]}...")
            
            print(f"\n📊 Summary:")
            print(f"   Total posts received: {posts_received}")
            print(f"   Expected posts: {len(test_data['target_platforms']) * 2}")  # Assuming ~2 topics per platform
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_regular_api_for_comparison():
    """Test the regular API for comparison"""
    print("\n🔄 Testing regular API for comparison...")
    
    test_data = {
        "text": "Artificial intelligence is revolutionizing the way we work and live.",
        "target_platforms": ["twitter"]
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/v1/generate-posts",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        end_time = time.time()
        
        print(f"📥 Regular API Response: {response.status_code}")
        print(f"⏱️  Total time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                platform_posts = data.get('platform_posts', {})
                total_posts = sum(len(posts) for posts in platform_posts.values())
                print(f"📊 Posts generated: {total_posts}")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Regular API test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Streaming API Tests\n")
    print("=" * 60)
    
    # Test streaming API
    test_streaming_posts()
    
    print("\n" + "=" * 60)
    
    # Test regular API for comparison
    test_regular_api_for_comparison()
    
    print("\n�� Tests completed!") 