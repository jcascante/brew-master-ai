# 🖥️ Backend Module

FastAPI server providing RAG (Retrieval-Augmented Generation) functionality with Claude API integration for the Brew Master AI chatbot.

## 🎯 Purpose

This module serves as the core API layer that:
- Handles user chat requests
- Performs semantic search in the vector database
- Generates natural language responses using Claude API
- Manages conversation context and sessions
- Provides health monitoring and error handling

## ✨ Features

### 🤖 RAG Architecture
- **Semantic Search**: Query Qdrant vector database for relevant content
- **Context Integration**: Combine retrieved chunks with user queries
- **Natural Responses**: Generate human-like answers using Claude API
- **Source Attribution**: Provide transparency about information sources
- **Confidence Scoring**: Assess response quality and relevance
- **Conversation Context**: Maintain session history for better follow-ups
- **Structured Fallbacks**: Graceful degradation when Claude API unavailable

### ⚡ Performance & Scalability
- **Async Operations**: Non-blocking I/O for high concurrency
- **Thread Pool Execution**: Heavy operations run in background threads
- **Connection Pooling**: Efficient database and API connections
- **Error Handling**: Graceful degradation and comprehensive logging

### 🔧 Developer Experience
- **Health Checks**: Detailed system status monitoring
- **Environment Configuration**: Flexible setup via .env files
- **API Documentation**: Auto-generated with FastAPI
- **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
# Qdrant running on localhost:6333
# Anthropic API key
```

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
echo "CLAUDE_MODEL=claude-3-haiku-20240307" >> .env
```

### Running the Server
```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "qdrant_connected": true,
  "collection_exists": true,
  "claude_available": true
}
```

### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "query": "What is the basic process of brewing beer?",
  "top_k": 3
}
```

**Response:**
```json
{
  "answer": "Based on the information available, beer brewing involves several key steps...",
  "sources": [
    {
      "source_file": "transcript1.txt",
      "score": 0.85,
      "text_preview": "The brewing process begins with malting..."
    }
  ],
  "confidence": 0.92,
  "quality": "high",
  "query": "What is the basic process of brewing beer?",
  "conversation_id": "session_123"
}
```

### Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "Hello from Brew Master AI Backend!"
}
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...              # Your Claude API key

# Optional
CLAUDE_MODEL=claude-3-haiku-20240307     # Model for responses
QDANT_HOST=localhost                      # Qdrant host
QDANT_PORT=6333                          # Qdrant port
COLLECTION_NAME=brew_master_ai           # Vector collection name
```

### Model Selection
- **Development**: `claude-3-haiku-20240307` (fastest, lowest cost)
- **Production**: `claude-3-sonnet-20240229` (balanced)
- **High Quality**: `claude-3-opus-20240229` (best quality, highest cost)

## 🏗️ Architecture

### Request Flow
```
User Query → FastAPI → Embed Query → Search Qdrant → 
Retrieve Chunks → Format Context → Call Claude API → 
Generate Response → Return to User
```

### Components
- **FastAPI App**: Main application server
- **Sentence Transformer**: Text embedding model
- **Qdrant Client**: Vector database connection
- **Claude Client**: Anthropic API integration
- **Async Thread Pool**: Background task execution

### Error Handling
- **API Key Missing**: Graceful fallback to raw chunks
- **Qdrant Unavailable**: 503 Service Unavailable
- **Claude API Errors**: Fallback response with chunks
- **Invalid Requests**: 400 Bad Request with details

## 🔧 Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

### Key Functions

#### `startup_event()`
- Initializes embedding model and database connections
- Validates configuration and dependencies
- Sets up global variables for reuse

#### `get_relevant_chunks(query, top_k)`
- Embeds user query using sentence-transformers
- Searches Qdrant for similar content
- Returns formatted chunk results

#### `generate_rag_response(query, chunks)`
- Formats retrieved chunks as context
- Creates prompt for Claude API
- Handles API calls and error fallbacks

#### `chat(request)`
- Main endpoint handler
- Orchestrates the complete RAG pipeline
- Returns structured response with sources

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Chat Request
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is beer brewing?", "top_k": 3}'
```

### Load Testing
```bash
# Install Apache Bench
brew install httpd  # macOS

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 -p test_payload.json -T application/json http://localhost:8000/chat
```

## 🔍 Monitoring

### Logs
The application provides comprehensive logging:
- **INFO**: Normal operations and request processing
- **WARNING**: Non-critical issues (missing API keys)
- **ERROR**: Critical failures and exceptions

### Metrics
- Request processing times
- Vector search performance
- Claude API response times
- Error rates and types

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### AWS Deployment
- **ECS**: Containerized deployment with load balancing
- **Lambda**: Serverless for low traffic
- **API Gateway**: For additional security and rate limiting

### Environment Setup
```bash
# Production environment variables
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-sonnet-20240229
QDANT_HOST=your-qdrant-host
QDANT_PORT=6333
```

## 🔒 Security

### API Key Management
- Store API keys in environment variables
- Never commit .env files to version control
- Use AWS Secrets Manager for production

### Rate Limiting
- Consider implementing rate limiting for public APIs
- Monitor Claude API usage and costs
- Set appropriate request size limits

### Input Validation
- Validate query length and content
- Sanitize user inputs
- Implement request size limits

## 🔧 Troubleshooting

### Common Issues

**Qdrant Connection Failed:**
```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# Restart Qdrant
cd ../vector-db && docker compose restart
```

**Claude API Errors:**
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Test API key
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages \
  -d '{"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "test"}]}'
```

**Model Loading Issues:**
- Check internet connection for model downloads
- Ensure sufficient disk space (~1GB for models)
- Verify Python environment and dependencies

## 📈 Performance Optimization

### Caching
- Embedding model is loaded once at startup
- Qdrant client connection is reused
- Consider Redis for session caching

### Async Operations
- All heavy operations use `asyncio.to_thread()`
- Non-blocking I/O for database and API calls
- Configurable thread pool sizes

### Resource Management
- Monitor memory usage with large models
- Implement connection pooling for external APIs
- Use appropriate worker processes for production

## 🔄 Integration

### Frontend Integration
The backend is designed to work with the React frontend:
- CORS enabled for local development
- JSON API responses
- Error handling for frontend consumption

### Data Pipeline Integration
- Expects Qdrant collection `brew_master_ai`
- Uses sentence-transformers embeddings
- Compatible with data-extraction module output

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
