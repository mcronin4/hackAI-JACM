import requests
import json
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_content(original_text, topics, original_url, platforms=["twitter"], base_url="http://localhost:8000"):
    """Generate social media content from topics"""
    
    url = f"{base_url}/api/v1/generate-content"
    
    data = {
        "original_text": original_text,
        "topics": topics,
        "original_url": original_url,
        "target_platforms": platforms
    }
    
    try:
        print("🚀 Generating content...")
        response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Generated {result['successful_generations']}/{result['total_generated']} posts")
            print(f"Processing time: {result['total_processing_time']:.1f}s")
            
            for content in result['generated_content']:
                if content['success']:
                    print(f"\n📝 Final Post ({content['platform']}):")
                    print("=" * 50)
                    print(content['final_post'])
                    print("=" * 50)
                    
                    # Calculate realistic character count (content + 23 for shortened URL + 1 space)
                    # Extract content length by removing the URL from final_post
                    final_post = content['final_post']
                    if ' https://' in final_post:
                        content_only = final_post.split(' https://')[0]
                        content_length = len(content_only)
                        realistic_total = content_length + 23 + 1  # content + shortened URL + space
                        
                        print(f"Content: {content_length} chars")
                        print(f"Realistic total: {realistic_total}/280 chars (with Twitter URL shortening)")
                        print(f"Utilization: {realistic_total/280*100:.1f}%")
                    else:
                        print(f"Characters: {len(final_post)}/280")
                        print(f"Utilization: {len(final_post)/280*100:.1f}%")
                else:
                    print(f"❌ Failed: {content['error']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_server_health(base_url="http://localhost:8000"):
    """Check if the server is running and healthy"""
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy and ready!")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("💡 Make sure to start the server with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return False

def run_examples():
    """Run example content generation scenarios"""
    
    print("🧪 Content Generation Examples")
    print("=" * 60)
    
    # Check server health first
    if not check_server_health():
        return
    
    print("\n📋 Example 1: Remote Work Productivity")
    print("-" * 40)
    
    original_text = """
    Remote work has transformed the modern workplace, but it comes with unique challenges. 
    Many professionals struggle with maintaining productivity while working from home. 
    Distractions, lack of proper workspace setup, and difficulty maintaining work-life 
    balance are common issues. However, with the right strategies, tools, and mindset, 
    remote workers can actually be more productive than their office counterparts.
    """
    
    topics = [
        {
            "topic_id": 1,
            "topic_name": "Remote Work Productivity Challenges",
            "content_excerpt": "Many professionals struggle with maintaining productivity while working from home due to distractions and workspace issues.",
            "primary_emotion": "Justify Their Failures",
            "emotion_confidence": 0.85,
            "reasoning": "This topic validates common struggles with remote work, allowing people to feel understood rather than blamed."
        }
    ]
    
    generate_content(
        original_text=original_text,
        topics=topics,
        original_url="https://example.com/remote-work-guide"
    )
    
    print("\n" + "="*60 + "\n")
    
    print("📋 Example 2: AI Technology")
    print("-" * 40)
    
    ai_text = """
    Artificial Intelligence is revolutionizing industries across the globe. From healthcare 
    to finance, AI tools are helping professionals work smarter and more efficiently. 
    However, many people are still uncertain about how to integrate AI into their daily 
    workflows and what the future holds for AI-human collaboration.
    """
    
    ai_topics = [
        {
            "topic_id": 2,
            "topic_name": "AI Integration in Daily Work",
            "content_excerpt": "Many professionals are uncertain about how to integrate AI tools into their daily workflows effectively.",
            "primary_emotion": "Anticipation",
            "emotion_confidence": 0.90,
            "reasoning": "This topic creates excitement about future possibilities and technological advancement."
        }
    ]
    
    generate_content(
        original_text=ai_text,
        topics=ai_topics,
        original_url="https://example.com/ai-integration-guide"
    )
    
    print("\n" + "="*60 + "\n")
    
    print("📋 Example 3: Entrepreneurship")
    print("-" * 40)
    
    startup_text = """
    Starting a business is one of the most challenging yet rewarding endeavors an individual 
    can undertake. The entrepreneurial journey is filled with ups and downs, requiring 
    resilience, creativity, and strategic thinking. Many aspiring entrepreneurs struggle 
    with finding the right idea, securing funding, and building a sustainable business model.
    """
    
    startup_topics = [
        {
            "topic_id": 3,
            "topic_name": "Entrepreneurship Challenges",
            "content_excerpt": "Many aspiring entrepreneurs struggle with finding the right idea, securing funding, and building sustainable business models.",
            "primary_emotion": "Hope",
            "emotion_confidence": 0.88,
            "reasoning": "This topic inspires hope and determination in aspiring entrepreneurs facing common challenges."
        }
    ]
    
    generate_content(
        original_text=startup_text,
        topics=startup_topics,
        original_url="https://example.com/startup-guide"
    )

def run_custom_example():
    """Run a custom example with user input"""
    print("\n🎯 Custom Content Generation")
    print("=" * 40)
    
    # Simple example with predefined data for quick testing
    custom_text = input("Enter your original text (or press Enter for default): ").strip()
    
    if not custom_text:
        custom_text = "This is a sample article about productivity and time management in the modern workplace."
    
    topic_name = input("Enter topic name (or press Enter for default): ").strip()
    if not topic_name:
        topic_name = "Productivity Tips"
    
    url = input("Enter your content URL (or press Enter for default): ").strip()
    if not url:
        url = "https://example.com/your-article"
    
    topics = [
        {
            "topic_id": 1,
            "topic_name": topic_name,
            "content_excerpt": custom_text[:100] + "...",
            "primary_emotion": "Anticipation",
            "emotion_confidence": 0.80,
            "reasoning": "This topic creates interest and engagement with the audience."
        }
    ]
    
    generate_content(
        original_text=custom_text,
        topics=topics,
        original_url=url
    )

if __name__ == "__main__":
    print("🚀 HackAI Content Generation System")
    print("Choose an option:")
    print("1. Run example scenarios")
    print("2. Run custom example")
    print("3. Check server health only")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        run_examples()
    elif choice == "2":
        if check_server_health():
            run_custom_example()
    elif choice == "3":
        check_server_health()
    else:
        print("Invalid choice. Running examples by default.")
        run_examples() 