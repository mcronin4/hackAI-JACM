"""
Test script to demonstrate parallelization improvements in the agent workflow.

This script compares the performance of:
1. Sequential processing (original approach)
2. Topic-level parallelization (new approach)
"""

import asyncio
import time
from datetime import datetime
from app.agents.agent_orchestrator import AgentOrchestrator
from app.services.content_pipeline import ContentPipelineService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample long-form content for testing
SAMPLE_TEXT = """
The future of artificial intelligence is rapidly evolving, transforming how we work, learn, and interact with technology. Machine learning algorithms are becoming more sophisticated, enabling computers to understand natural language, recognize patterns in data, and make predictions with increasing accuracy.

One of the most significant developments in AI is the emergence of large language models like GPT and Claude. These models can generate human-like text, answer complex questions, and assist with various tasks from writing to coding. The implications for education, content creation, and business operations are profound.

However, with great power comes great responsibility. As AI systems become more capable, we must address important ethical considerations including bias, privacy, and the potential displacement of human workers. It's crucial that we develop AI systems that are transparent, fair, and aligned with human values.

The democratization of AI tools is another important trend. What once required teams of PhD researchers and massive computing resources is now accessible to individuals and small businesses. This accessibility is spurring innovation across industries, from healthcare to entertainment.

Looking ahead, we can expect to see AI integrated into more aspects of our daily lives. Smart homes will become truly intelligent, autonomous vehicles will become commonplace, and AI assistants will become even more helpful and natural to interact with.

The key to successful AI adoption lies in finding the right balance between automation and human creativity. While AI can handle routine tasks and process vast amounts of information, human insight, empathy, and creative thinking remain irreplaceable.

As we navigate this AI-powered future, continuous learning and adaptation will be essential. The skills that matter most will be those that complement AI capabilities rather than compete with them. Critical thinking, emotional intelligence, and the ability to work alongside AI systems will become increasingly valuable.
"""

async def test_sequential_vs_parallel():
    """Test sequential vs parallel processing performance"""
    
    print("🚀 Testing Agent Workflow Parallelization")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(temperature=0.1)
    
    print(f"📝 Input text: {len(SAMPLE_TEXT)} characters")
    print(f"🎯 Testing with max_topics=5")
    print()
    
    # Test 1: Sequential processing (original)
    print("🔄 Test 1: Sequential Processing (Original)")
    print("-" * 40)
    
    start_time = time.time()
    sequential_result = orchestrator.process_text(SAMPLE_TEXT, max_topics=5)
    sequential_time = time.time() - start_time
    
    if sequential_result['workflow_summary']['status'] == 'completed':
        print(f"✅ Sequential processing completed in {sequential_time:.2f}s")
        print(f"📊 Topics extracted: {sequential_result['workflow_summary']['topics_extracted']}")
        print(f"🎭 Emotions analyzed: {sequential_result['workflow_summary']['emotions_analyzed']}")
        print(f"⏱️ Topic extraction: {sequential_result['topic_extraction']['processing_time']:.2f}s")
        print(f"⏱️ Emotion analysis: {sequential_result['emotion_targeting']['processing_time']:.2f}s")
    else:
        print(f"❌ Sequential processing failed: {sequential_result['workflow_summary']['error_message']}")
    
    print()
    
    # Test 2: Parallel processing (new)
    print("⚡ Test 2: Topic-Level Parallel Processing (New)")
    print("-" * 40)
    
    start_time = time.time()
    parallel_result = await orchestrator.process_text_parallel(SAMPLE_TEXT, max_topics=5)
    parallel_time = time.time() - start_time
    
    if parallel_result['workflow_summary']['status'] == 'completed':
        print(f"✅ Parallel processing completed in {parallel_time:.2f}s")
        print(f"📊 Topics extracted: {parallel_result['workflow_summary']['topics_extracted']}")
        print(f"🎭 Emotions analyzed: {parallel_result['workflow_summary']['emotions_analyzed']}")
        print(f"⏱️ Topic extraction: {parallel_result['topic_extraction']['processing_time']:.2f}s")
        print(f"⏱️ Emotion analysis (parallel): {parallel_result['emotion_targeting']['processing_time']:.2f}s")
        print(f"🔧 Parallel execution: {parallel_result['emotion_targeting']['parallel_execution']}")
    else:
        print(f"❌ Parallel processing failed: {parallel_result['workflow_summary']['error_message']}")
    
    print()
    
    # Performance comparison
    if (sequential_result['workflow_summary']['status'] == 'completed' and 
        parallel_result['workflow_summary']['status'] == 'completed'):
        
        speedup = sequential_time / parallel_time
        time_saved = sequential_time - parallel_time
        improvement_percent = ((sequential_time - parallel_time) / sequential_time) * 100
        
        print("📈 Performance Comparison")
        print("-" * 40)
        print(f"Sequential time: {sequential_time:.2f}s")
        print(f"Parallel time:   {parallel_time:.2f}s")
        print(f"Time saved:      {time_saved:.2f}s")
        print(f"Speedup:         {speedup:.2f}x")
        print(f"Improvement:     {improvement_percent:.1f}%")
        
        if speedup > 1.1:
            print("🎉 Significant performance improvement with parallelization!")
        elif speedup > 1.0:
            print("✅ Modest performance improvement with parallelization")
        else:
            print("⚠️ No significant performance improvement (may be due to overhead)")

async def test_content_pipeline_parallelization():
    """Test the full content pipeline with parallelization"""
    
    print("\n" + "=" * 60)
    print("🔄 Testing Full Content Pipeline Parallelization")
    print("=" * 60)
    
    # Initialize content pipeline
    pipeline = ContentPipelineService()
    
    # Mock context posts (empty for this test)
    context_posts = {
        "twitter": [],
        "linkedin": []
    }
    
    start_time = time.time()
    
    try:
        result = await pipeline.process_content(
            text=SAMPLE_TEXT,
            context_posts=context_posts,
            target_platforms=["twitter", "linkedin"],
            original_url="https://example.com/ai-future"
        )
        
        processing_time = time.time() - start_time
        
        if result['success']:
            print(f"✅ Full pipeline completed in {processing_time:.2f}s")
            print(f"📊 Metadata: {result['metadata']}")
            
            total_posts = sum(len(posts) for posts in result['platform_posts'].values())
            print(f"📝 Total posts generated: {total_posts}")
            
            for platform, posts in result['platform_posts'].items():
                print(f"🐦 {platform}: {len(posts)} posts")
                for i, post in enumerate(posts, 1):
                    print(f"   Post {i}: {post['post_content'][:100]}...")
        else:
            print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Pipeline exception: {str(e)}")

def main():
    """Main test function"""
    print("🧪 Agent Parallelization Test Suite")
    print("Testing topic-level parallelization improvements")
    print()
    
    # Run the async tests
    asyncio.run(test_sequential_vs_parallel())
    asyncio.run(test_content_pipeline_parallelization())
    
    print("\n✨ Test suite completed!")

if __name__ == "__main__":
    main() 