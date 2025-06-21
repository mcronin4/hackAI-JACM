# Topic Extraction API with LangGraph

A FastAPI backend that uses LangGraph agents to extract topics from text content. The system identifies distinct topics, extracts relevant excerpts, and provides confidence scores in a structured JSON format.

## Features

- **LangGraph Agent**: Multi-node workflow for robust topic extraction
- **FastAPI Backend**: Modern, async API with automatic documentation
- **Structured Output**: JSON response with topic_id, topic_name, content_excerpt, and confidence_score
- **Error Handling**: Comprehensive error handling and validation
- **Testing**: Unit tests for reliability
- **Health Monitoring**: Built-in health check endpoints

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   LangGraph      │    │   OpenAI        │
│   Backend       │───▶│   Agent          │───▶│   LLM           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │   Topic         │
         │              │   Extraction    │
         │              │   Workflow      │
         │              └─────────────────┘
         │
    ┌────▼────┐
    │  JSON   │
    │Response │
    └─────────┘
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hackAI-JACM
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/api/v1/extract-topics`
Extract topics from text using LangGraph agent.

**Request Body:**
```json
{
  "text": "Your text content here...",
  "max_topics": 10
}
```

**Response:**
```json
{
  "topics": [
    {
      "topic_id": 1,
      "topic_name": "Artificial Intelligence",
      "content_excerpt": "AI has revolutionized many industries...",
      "confidence_score": 0.95
    }
  ],
  "total_topics": 1,
  "processing_time": 1.23
}
```

### GET `/api/v1/health`
Health check endpoint.

### GET `/api/v1/topics/example`
Get example response format.

### GET `/docs`
Interactive API documentation (Swagger UI).

## LangGraph Workflow

The topic extraction uses a 3-node LangGraph workflow:

1. **Extract Topics Node**: Uses OpenAI LLM to identify topics and extract excerpts
2. **Validate Topics Node**: Validates and cleans extracted topic data
3. **Format Response Node**: Prepares final response structure

## Configuration

Environment variables in `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_NAME=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.1

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Usage Examples

### Python Client
```python
import requests

url = "http://localhost:8000/api/v1/extract-topics"
data = {
    "text": "Artificial intelligence and machine learning are transforming the technology landscape. Deep learning models have achieved remarkable results in computer vision and natural language processing.",
    "max_topics": 3
}

response = requests.post(url, json=data)
topics = response.json()
print(f"Extracted {topics['total_topics']} topics")
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/extract-topics" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your text content here...",
       "max_topics": 5
     }'
```

## Development

### Project Structure
```
hackAI-JACM/
├── app/
│   ├── agents/
│   │   └── topic_extractor.py    # LangGraph agent
│   ├── api/
│   │   └── routes.py             # FastAPI routes
│   ├── models.py                 # Pydantic models
│   └── services/
│       └── topic_service.py      # Business logic
├── tests/
│   └── test_topic_extractor.py   # Unit tests
├── main.py                       # FastAPI app
├── requirements.txt              # Dependencies
└── README.md
```

### Adding New Features

1. **New Agent Nodes**: Add to `app/agents/topic_extractor.py`
2. **New Endpoints**: Add to `app/api/routes.py`
3. **New Models**: Add to `app/models.py`
4. **New Services**: Add to `app/services/`

## Production Deployment

1. **Environment**: Set `APP_ENV=production`
2. **CORS**: Configure allowed origins in `main.py`
3. **Logging**: Configure production logging
4. **Monitoring**: Add health checks and metrics
5. **Security**: Implement proper authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.