#!/usr/bin/env python3
"""
🎯 TopicExtractorAgent Test Runner
========================================
Comprehensive test suite for the TopicExtractorAgent with various test cases.
"""

import os
import json
from dotenv import load_dotenv
from app.agents.topic_extractor import TopicExtractorAgent

# Load environment variables
load_dotenv()

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{title}")
    print("=" * len(title))

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n{title}")
    print("-" * len(title))

def print_topic(topic: dict, index: int = None):
    """Print a topic in a formatted way"""
    if index is not None:
        print(f"Topic {index}: {topic['topic_name']}")
    else:
        print(f"Topic {topic['topic_id']}: {topic['topic_name']}")
    print(f"   Confidence: {topic['confidence_score']:.2f}")
    print(f"   Excerpt: {topic['content_excerpt'][:100]}...")
    print()

def test_api_key():
    """Test if API key is properly configured"""
    print_header("🔑 API Key Configuration Test")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        return False
    elif api_key == "your_google_api_key_here":
        print("❌ GOOGLE_API_KEY is still set to placeholder value")
        return False
    elif not api_key.startswith("AIza"):
        print("❌ GOOGLE_API_KEY doesn't look like a valid Google API key")
        return False
    else:
        print(f"✅ GOOGLE_API_KEY found (length: {len(api_key)} chars)")
        return True

def test_agent_initialization():
    """Test agent initialization"""
    print_header("🤖 Agent Initialization Test")
    
    try:
        agent = TopicExtractorAgent(temperature=0.1)
        print("✅ TopicExtractorAgent initialized successfully")
        print(f"   Model: gemini-1.5-flash")
        print(f"   Temperature: {agent.temperature}")
        return agent
    except Exception as e:
        print(f"❌ Failed to initialize TopicExtractorAgent: {str(e)}")
        return None

def test_basic_extraction(agent: TopicExtractorAgent):
    """Test basic topic extraction"""
    print_header("📋 Basic Topic Extraction Test")
    
    sample_text = """
    Artificial Intelligence (AI) has revolutionized the way we approach problem-solving in various industries. 
    Machine learning algorithms, a subset of AI, enable computers to learn from data without being explicitly programmed. 
    Deep learning, which uses neural networks with multiple layers, has achieved remarkable success in image recognition, 
    natural language processing, and autonomous vehicles. The field of computer vision has made significant strides, 
    allowing machines to interpret and understand visual information from the world around them. 
    Natural Language Processing (NLP) has enabled computers to understand, interpret, and generate human language, 
    leading to advancements in chatbots, translation services, and text analysis tools.
    """
    
    print("Input Text:")
    print("-" * 50)
    print(sample_text.strip())
    print("-" * 50)
    
    try:
        result = agent.extract_topics(sample_text, max_topics=5)
        
        if result['success']:
            print(f"✅ Success! Found {result['total_topics']} topics in {result['processing_time']:.2f} seconds")
            print("\nExtracted Topics:")
            for topic in result['topics']:
                print_topic(topic)
        else:
            print(f"❌ Error: {result['error']}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Exception during extraction: {str(e)}")
        return False

def test_short_text(agent: TopicExtractorAgent):
    """Test extraction from short text"""
    print_header("📝 Short Text Test")
    
    short_text = "Climate change is affecting global weather patterns. Scientists are studying the impact on ecosystems."
    
    print(f"Input: {short_text}")
    
    try:
        result = agent.extract_topics(short_text, max_topics=3)
        
        if result['success']:
            print(f"✅ Success! Found {result['total_topics']} topics")
            for topic in result['topics']:
                print_topic(topic)
        else:
            print(f"❌ Error: {result['error']}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_long_text(agent: TopicExtractorAgent):
    """Test extraction from long text"""
    print_header("📚 Long Text Test")
    
    long_text = """
    The Internet of Things (IoT) represents a paradigm shift in how we interact with technology. 
    By connecting everyday objects to the internet, IoT enables unprecedented levels of automation and data collection. 
    Smart homes, equipped with IoT devices, can automatically adjust lighting, temperature, and security based on user preferences and environmental conditions. 
    In healthcare, IoT devices monitor patient vital signs in real-time, enabling early detection of health issues and improving treatment outcomes. 
    Industrial IoT (IIoT) transforms manufacturing processes through predictive maintenance, quality control, and supply chain optimization. 
    However, the proliferation of IoT devices also raises significant cybersecurity concerns, as each connected device represents a potential entry point for malicious actors. 
    Data privacy is another critical issue, as IoT devices collect vast amounts of personal information that must be protected. 
    The energy sector benefits from IoT through smart grid technology, which optimizes power distribution and reduces waste. 
    Transportation systems leverage IoT for traffic management, vehicle tracking, and autonomous driving capabilities. 
    Environmental monitoring uses IoT sensors to track air quality, water quality, and wildlife populations, providing valuable data for conservation efforts.
    """
    
    print("Testing with long text (multiple paragraphs)...")
    
    try:
        result = agent.extract_topics(long_text, max_topics=8)
        
        if result['success']:
            print(f"✅ Success! Found {result['total_topics']} topics in {result['processing_time']:.2f} seconds")
            for topic in result['topics']:
                print_topic(topic)
        else:
            print(f"❌ Error: {result['error']}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_edge_cases(agent: TopicExtractorAgent):
    """Test edge cases and error handling"""
    print_header("⚠️ Edge Cases Test")
    
    test_cases = [
        {
            "name": "Empty Text",
            "text": "",
            "max_topics": 5
        },
        {
            "name": "Very Short Text",
            "text": "AI",
            "max_topics": 3
        },
        {
            "name": "Single Topic Text",
            "text": "Machine learning is a subset of artificial intelligence.",
            "max_topics": 5
        },
        {
            "name": "Repetitive Text",
            "text": "AI AI AI AI AI AI AI AI AI AI AI AI AI AI AI AI AI AI AI AI",
            "max_topics": 3
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print_section(f"Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['text']}'")
        print(f"Max Topics: {test_case['max_topics']}")
        
        try:
            result = agent.extract_topics(test_case['text'], test_case['max_topics'])
            
            if result['success']:
                print(f"✅ Success! Found {result['total_topics']} topics")
                for topic in result['topics']:
                    print_topic(topic)
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print()

def test_performance(agent: TopicExtractorAgent):
    """Test performance with different parameters"""
    print_header("⚡ Performance Test")
    
    test_text = """
    Blockchain technology has emerged as a revolutionary force in digital transactions and data management. 
    By creating decentralized, immutable ledgers, blockchain ensures transparency and security in financial transactions. 
    Cryptocurrencies like Bitcoin and Ethereum leverage blockchain for peer-to-peer transactions without intermediaries. 
    Smart contracts, self-executing agreements on blockchain platforms, automate complex business processes and reduce costs. 
    Supply chain management benefits from blockchain's ability to track products from origin to consumer, ensuring authenticity and reducing fraud. 
    Healthcare systems use blockchain to secure patient records and enable secure sharing between providers. 
    Voting systems can leverage blockchain for transparent and tamper-proof elections. 
    However, blockchain faces challenges including scalability issues, high energy consumption, and regulatory uncertainty.
    """
    
    temperatures = [0.0, 0.1, 0.5, 1.0]
    max_topics_list = [3, 5, 10]
    
    print("Testing with different temperatures and max_topics values...")
    
    for temp in temperatures:
        for max_topics in max_topics_list:
            print_section(f"Temperature: {temp}, Max Topics: {max_topics}")
            
            try:
                # Create new agent with different temperature
                test_agent = TopicExtractorAgent(temperature=temp)
                result = test_agent.extract_topics(test_text, max_topics)
                
                if result['success']:
                    print(f"✅ Success! Found {result['total_topics']} topics in {result['processing_time']:.2f} seconds")
                    print(f"   Average confidence: {sum(t['confidence_score'] for t in result['topics']) / len(result['topics']):.2f}")
                else:
                    print(f"❌ Error: {result['error']}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
            
            print()

def save_results(agent: TopicExtractorAgent):
    """Save test results to JSON file"""
    print_header("💾 Results Export Test")
    
    sample_text = """
    Renewable energy sources are becoming increasingly important in the global energy mix. 
    Solar power, harnessed through photovoltaic panels, converts sunlight directly into electricity. 
    Wind energy uses turbines to capture kinetic energy from moving air masses. 
    Hydroelectric power generates electricity from flowing water in rivers and dams. 
    Geothermal energy taps into the Earth's internal heat for power generation. 
    These renewable sources offer sustainable alternatives to fossil fuels, reducing greenhouse gas emissions. 
    However, renewable energy faces challenges including intermittency, storage limitations, and infrastructure costs. 
    Battery technology is advancing rapidly to address energy storage needs for renewable systems.
    """
    
    try:
        result = agent.extract_topics(sample_text, max_topics=6)
        
        if result['success']:
            # Add metadata
            export_data = {
                "test_info": {
                    "agent_type": "TopicExtractorAgent",
                    "model": "gemini-1.5-flash",
                    "temperature": agent.temperature,
                    "timestamp": str(result.get('processing_time', 0))
                },
                "input_text": sample_text.strip(),
                "extraction_results": result
            }
            
            # Save to file
            with open("topic_extraction_results.json", "w") as f:
                json.dump(export_data, f, indent=2)
            
            print("✅ Results saved to topic_extraction_results.json")
            print(f"   Found {result['total_topics']} topics")
            print(f"   Processing time: {result['processing_time']:.2f} seconds")
            
            return True
        else:
            print(f"❌ Error during extraction: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during export: {str(e)}")
        return False

def main():
    """Main test runner"""
    print_header("🎯 TopicExtractorAgent Test Runner")
    print("=" * 50)
    
    # Test API key
    if not test_api_key():
        print("\n❌ API key test failed. Please check your configuration.")
        return
    
    # Test agent initialization
    agent = test_agent_initialization()
    if not agent:
        print("\n❌ Agent initialization failed.")
        return
    
    # Run all tests
    tests = [
        ("Basic Extraction", lambda: test_basic_extraction(agent)),
        ("Short Text", lambda: test_short_text(agent)),
        ("Long Text", lambda: test_long_text(agent)),
        ("Edge Cases", lambda: test_edge_cases(agent)),
        ("Performance", lambda: test_performance(agent)),
        ("Results Export", lambda: save_results(agent))
    ]
    
    print_header("🧪 Running All Tests")
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print_section(f"Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
    
    # Summary
    print_header("📊 Test Summary")
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Your TopicExtractorAgent is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 