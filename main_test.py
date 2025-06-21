#!/usr/bin/env python3
"""
Simple test script for the EmotionTargetingAgent
Tests emotion targeting analysis with mock topic input.

Usage:
    python main_test.py
"""

import os
import json
from typing import Dict, List, Any

from dotenv import load_dotenv
load_dotenv()


def create_mock_topics() -> List[Dict[str, Any]]:
    """Create mock topic data for testing the emotion targeting pipeline"""
    return [
        {
            "topic_id": 1,
            "topic_name": "Remote Work Productivity Challenges",
            "content_excerpt": "Many professionals report feeling guilty about their decreased productivity levels, often blaming themselves for lacking discipline or focus when working from home.",
            "confidence_score": 0.89
        },
        {
            "topic_id": 2,
            "topic_name": "Ineffective Communication Tools",
            "content_excerpt": "Organizations rushed to implement remote work solutions without properly evaluating their effectiveness or providing adequate training to employees.",
            "confidence_score": 0.82
        },
        {
            "topic_id": 3,
            "topic_name": "Loss of Social Workplace Connections", 
            "content_excerpt": "The informal conversations, spontaneous brainstorming sessions, and casual networking opportunities that naturally occur in physical workspaces are difficult to replicate virtually.",
            "confidence_score": 0.76
        }
    ]


def test_emotion_targeting():
    """Test the EmotionTargetingAgent with mock topics"""
    print("🎭 Testing EmotionTargetingAgent Pipeline")
    print("=" * 50)
    
    # Step 1: Show input data
    mock_topics = create_mock_topics()
    
    print("📋 Input Topics:")
    print("-" * 20)
    for topic in mock_topics:
        print(f"Topic {topic['topic_id']}: {topic['topic_name']}")
        print(f"   Confidence: {topic['confidence_score']:.2f}")
        print(f"   Excerpt: {topic['content_excerpt'][:80]}...")
        print()
    
    # Step 2: Test EmotionTargetingAgent
    print("🎯 Running Emotion Analysis:")
    print("-" * 30)
    
    try:
        from app.agents import EmotionTargetingAgent
        
        # Create the agent
        emotion_agent = EmotionTargetingAgent()
        print("✅ EmotionTargetingAgent created successfully")
        
        # Run the analysis
        print("🔄 Analyzing emotions with Gemini API...")
        emotion_result = emotion_agent.analyze_emotions(mock_topics)
        
        if emotion_result['success']:
            print(f"✅ Analysis completed successfully!")
            print(f"📊 Analyzed {emotion_result['total_analyzed']} topics")
            print(f"⏱️  Processing time: {emotion_result['processing_time']:.2f} seconds")
            
            print("\n🎭 Emotion Analysis Results:")
            print("-" * 35)
            
            emotion_counts = {}
            for analysis in emotion_result['emotion_analysis']:
                emotion_display = analysis['primary_emotion'].replace('_', ' ').title()
                emotion_counts[emotion_display] = emotion_counts.get(emotion_display, 0) + 1
                
                print(f"\n📌 Topic: {analysis['topic_name']}")
                print(f"🎯 Target Emotion: {emotion_display}")
                print(f"📊 Confidence: {analysis['emotion_confidence']:.2f}")
                print(f"💭 Reasoning: {analysis['reasoning']}")
                print("-" * 50)
            
            print(f"\n📈 Summary:")
            print(f"   Total Topics: {emotion_result['total_analyzed']}")
            print(f"   Processing Time: {emotion_result['processing_time']:.2f}s")
            print(f"   Emotion Distribution:")
            for emotion, count in emotion_counts.items():
                print(f"     • {emotion}: {count} topic(s)")
            
            # Save results
            with open('emotion_analysis_results.json', 'w') as f:
                json.dump(emotion_result, f, indent=2)
            print(f"\n💾 Results saved to 'emotion_analysis_results.json'")
            
        else:
            print(f"❌ Emotion analysis failed!")
            print(f"Error: {emotion_result['error']}")
            
    except Exception as e:
        print(f"❌ Error running EmotionTargetingAgent:")
        print(f"   {type(e).__name__}: {str(e)}")
        
        # Check for common issues
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("\n🔑 GOOGLE_API_KEY not found!")
            print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        else:
            print(f"\n🔑 GOOGLE_API_KEY is set (length: {len(api_key)} characters)")
            
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Make sure GOOGLE_API_KEY is set and valid")
        print(f"   2. Check your Google AI Studio API key permissions")
        print(f"   3. Verify you have credits/quota available")


def main():
    """Main test function"""
    print("🎯 EmotionTargetingAgent Test Runner")
    print("=" * 40)
    
    # Check API key status
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"🔑 GOOGLE_API_KEY found (length: {len(api_key)} chars)")
    else:
        print("⚠️  GOOGLE_API_KEY not found")
    
    print()
    test_emotion_targeting()
    print(f"\n✨ Test completed!")


if __name__ == "__main__":
    main() 