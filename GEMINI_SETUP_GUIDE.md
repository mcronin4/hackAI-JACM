# Gemini Topic Extractor Setup Guide

## 🚀 Quick Start

### 1. Get Your Free Google AI API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (it looks like: `AIzaSyC...`)

### 2. Set Up Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your API key
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Example

```bash
python simple_gemini_example.py
```

## 📝 How to Use the Agent

### Basic Usage

```python
from app.agents.topic_extractor import TopicExtractorAgent

# Create the agent
agent = TopicExtractorAgent(temperature=0.1)

# Extract topics from your text
result = agent.extract_topics(
    text="Your text here...",
    max_topics=5
)

# Check if successful
if result['success']:
    for topic in result['topics']:
        print(f"Topic: {topic['topic_name']}")
        print(f"Excerpt: {topic['content_excerpt']}")
        print(f"Confidence: {topic['confidence_score']}")
```

### Input Parameters

- **`text`** (required): The text you want to analyze
- **`max_topics`** (optional): Maximum number of topics to extract (default: 10)

### Output Structure

```python
{
    'success': True,                    # Boolean: whether extraction succeeded
    'topics': [                        # List of extracted topics
        {
            'topic_id': 1,             # Sequential ID
            'topic_name': 'AI',        # Topic name
            'content_excerpt': '...',  # Relevant text excerpt
            'confidence_score': 0.95   # Confidence (0.0 to 1.0)
        }
    ],
    'total_topics': 1,                 # Number of topics found
    'processing_time': 1.23,           # Time taken in seconds
    'error': None                      # Error message if any
}
```

## 🔧 Configuration Options

### Temperature
Control how creative vs. focused the model is:
- `0.0`: Very focused, consistent results
- `0.1`: Balanced (recommended)
- `1.0`: More creative, varied results

```python
agent = TopicExtractorAgent(temperature=0.1)
```

### Model
The agent uses `gemini-1.5-flash` by default (free tier). You can change this in the code if needed.

## 📊 Example Output

```
=== Gemini Topic Extractor (Free Tier) ===

Input Text:
--------------------------------------------------
Artificial Intelligence (AI) has revolutionized the way we approach problem-solving in various industries. 
Machine learning algorithms, a subset of AI, enable computers to learn from data without being explicitly programmed. 
Deep learning, which uses neural networks with multiple layers, has achieved remarkable success in image recognition, 
natural language processing, and autonomous vehicles.

📊 Results:
==================================================
✅ Success! Found 3 topics
⏱️  Processing time: 1.23 seconds
🔍 Model used: gemini-1.5-flash

📋 Extracted Topics:
--------------------------------------------------
Topic 1: Artificial Intelligence
Confidence: 0.95
Excerpt: Artificial Intelligence (AI) has revolutionized the way we approach problem-solving in various industries.
------------------------------
Topic 2: Machine Learning
Confidence: 0.88
Excerpt: Machine learning algorithms, a subset of AI, enable computers to learn from data without being explicitly programmed.
------------------------------
Topic 3: Deep Learning
Confidence: 0.92
Excerpt: Deep learning, which uses neural networks with multiple layers, has achieved remarkable success in image recognition, natural language processing, and autonomous vehicles.
------------------------------
```

## 🛠️ Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not found"**
   - Make sure you've added your API key to the `.env` file
   - Check that the key starts with `AIzaSy`

2. **"Could not parse JSON response"**
   - This is normal - the agent has fallback parsing
   - If it persists, try reducing the temperature

3. **"Rate limit exceeded"**
   - Free tier has limits, wait a moment and try again
   - Consider upgrading to paid tier for higher limits

### Error Handling

The agent always returns a structured response, even on errors:

```python
result = agent.extract_topics("Some text...")

if result['success']:
    # Process topics
    topics = result['topics']
else:
    # Handle error
    print(f"Error: {result['error']}")
```

## 🎯 LangGraph Workflow

The agent uses a 3-node workflow:

1. **Extract Topics Node**: Gemini analyzes text and identifies topics
2. **Validate Topics Node**: Validates and cleans the extracted data
3. **Format Response Node**: Prepares the final response

This ensures robust, reliable topic extraction even if the LLM response isn't perfectly formatted.

## 💡 Tips

- **Text Length**: Works best with 100-2000 words
- **Topic Count**: Start with 3-5 topics for best results
- **Temperature**: Use 0.1 for consistent results
- **Error Handling**: Always check `result['success']` before processing

## 🔗 Resources

- [Google AI Studio](https://makersuite.google.com/app/apikey)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) 