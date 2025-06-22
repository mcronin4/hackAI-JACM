#!/usr/bin/env python3

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.content_pipeline import ContentPipelineService

async def test_platform_separated_response():
    """Test the new platform-separated response structure"""
    print("🧪 Testing Platform-Separated Response Structure")
    print("=" * 60)
    
    # Initialize the pipeline
    pipeline = ContentPipelineService()
    
    # Test content
    test_text = "Building strong professional relationships isn't just about networking events. It's about being genuinely curious about others and their challenges. When you shift from 'what can I get' to 'how can I help,' people notice."
    
    # Test with both platforms
    result = await pipeline.process_content(
        text=test_text,
        original_url="https://example.com/networking-tips",
        target_platforms=["twitter", "linkedin"]
    )
    
    if result['success']:
        print("✅ Pipeline Success!")
        print(f"📊 Total Topics: {result['total_topics']}")
        print(f"🎯 Successful Generations: {result['successful_generations']}")
        print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
        print()
        
        # Show the NEW platform-separated structure
        print("🆕 NEW STRUCTURE - platform_posts:")
        print("=" * 40)
        
        platform_posts = result['platform_posts']
        for platform, posts in platform_posts.items():
            print(f"\n📱 {platform.upper()} POSTS ({len(posts)} posts):")
            print("-" * 30)
            
            for i, post in enumerate(posts, 1):
                print(f"Post {i}:")
                print(f"  Content: {post['post_content'][:100]}...")
                print(f"  Topic ID: {post['topic_id']}")
                print(f"  Topic: {post['topic_name'][:50]}...")
                print(f"  Emotion: {post['primary_emotion']}")
                print(f"  Strategy: {post['content_strategy']}")
                print(f"  Length: {len(post['post_content'])} chars")
                print()
        
        # Show backwards compatibility
        print("\n🔄 LEGACY COMPATIBILITY - generated_posts:")
        print("=" * 40)
        print(f"Flat list with {len(result['generated_posts'])} posts:")
        for i, post in enumerate(result['generated_posts'], 1):
            print(f"  {i}. {post[:60]}...")
        
        # Show JSON structure for frontend
        print("\n📄 JSON STRUCTURE FOR FRONTEND:")
        print("=" * 40)
        
        # Create a simplified version for frontend demo
        frontend_structure = {
            'success': result['success'],
            'platform_posts': {
                platform: [
                    {
                        'content': post['post_content'],
                        'topic_id': post['topic_id'],
                        'emotion': post['primary_emotion'],
                        'strategy': post['content_strategy'],
                        'char_count': len(post['post_content'])
                    }
                    for post in posts
                ]
                for platform, posts in platform_posts.items()
            },
            'total_topics': result['total_topics'],
            'processing_time': result['processing_time']
        }
        
        print(json.dumps(frontend_structure, indent=2))
        
    else:
        print(f"❌ Pipeline Failed: {result['error']}")
        print("Error response structure:")
        print(json.dumps(result, indent=2))

def main():
    """Run the platform separation test"""
    import asyncio
    asyncio.run(test_platform_separated_response())

if __name__ == "__main__":
    main() 