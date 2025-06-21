#!/usr/bin/env python3
"""
Example usage of TopicExtractorAgent with Gemini 2.5
"""

import os
from dotenv import load_dotenv
from app.agents.topic_extractor import TopicExtractorAgent

# Load environment variables
load_dotenv()

def main():
    # Example text to extract topics from
    sample_text = """
    Artificial Intelligence (AI) has revolutionized the way we approach problem-solving in various industries. 
    Machine learning algorithms, a subset of AI, enable computers to learn from data without being explicitly programmed. 
    Deep learning, which uses neural networks with multiple layers, has achieved remarkable success in image recognition, 
    natural language processing, and autonomous vehicles. The field of computer vision has made significant strides, 
    allowing machines to interpret and understand visual information from the world around them. 
    Natural Language Processing (NLP) has enabled computers to understand, interpret, and generate human language, 
    leading to advancements in chatbots, translation services, and text analysis tools.
    """
    
    print("=== Topic Extraction with Gemini 2.5 ===\n")
    
    # Initialize agent with Gemini
    try:
        agent = TopicExtractorAgent(
            provider="gemini",
            model_name="gemini-1.5-pro",  # You can also use "gemini-1.5-flash" for faster responses
            temperature=0.5
        )
        
        print("Agent initialized successfully!")
        print(f"Provider: {agent.provider}")
        print(f"Model: {agent.llm.model}")
        print(f"Temperature: {agent.temperature}\n")
        
        # Extract topics
        print("Extracting topics...")
        result = agent.extract_topics(sample_text, max_topics=5)
        
        # Display results
        if result['success']:
            print(f"✅ Success! Found {result['total_topics']} topics in {result['processing_time']:.2f} seconds\n")
            
            for topic in result['topics']:
                print(f"Topic {topic['topic_id']}: {topic['topic_name']}")
                print(f"Confidence: {topic['confidence_score']:.2f}")
                print(f"Excerpt: {topic['content_excerpt']}")
                print("-" * 50)
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("\nMake sure you have:")
        print("1. Set GOOGLE_API_KEY in your .env file")
        print("2. Installed the required dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 