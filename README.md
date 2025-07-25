# 🍺 Brew Master AI

A comprehensive RAG (Retrieval-Augmented Generation) chatbot for beer brewing knowledge, built with modern AI technologies and designed for scalability.

## 🎯 Overview

Brew Master AI is an intelligent chatbot that provides expert knowledge about beer brewing processes, history, and brewery creation. It combines:

- **Multimodal Data Processing**: Videos, PowerPoint presentations, and text
- **Advanced RAG Architecture**: Vector search + Claude API for natural responses
- **Scalable Backend**: FastAPI with async operations and error handling
- **Modern Frontend**: React + Vite for responsive web interface

## ✨ Features

### 🤖 AI-Powered Chat
- Natural language queries about beer brewing
- Context-aware responses using retrieved knowledge
- Source attribution for transparency
- Confidence scoring and response quality indicators
- Conversation context for follow-up questions
- Export and sharing capabilities

### 📊 Data Processing Pipeline
- **Video Processing**: Extract audio and transcribe to text
- **Presentation Processing**: Extract images and perform OCR
- **Vector Embeddings**: Create semantic search capabilities
- **Batch Processing**: Handle multiple files efficiently

### 🏗️ Architecture
- **Monorepo Structure**: Organized modules for maintainability
- **Microservices Ready**: Backend can be containerized and scaled
- **Cloud-Native**: Designed for AWS deployment
- **Performance Optimized**: Async operations and connection pooling

## 🏛️ Project Structure

```
brew-master-ai/
├── 📁 data-extraction/     # CLI tools for data processing
├── 📁 backend/            # FastAPI RAG server
├── 📁 frontend/           # React chatbot interface
├── 📁 vector-db/          # Qdrant Docker configuration
├── 📄 CHECKPOINT.md       # Development progress tracker
└── 📄 README.md           # This file
```

## 📊 Current Status

### ✅ Phase 1: Core Experience - COMPLETE
- **Better Fallback Responses** - Structured, readable responses when Claude API unavailable
- **Export & Sharing Features** - Export conversations, copy responses, share chats
- **Enhanced RAG Pipeline** - Confidence scoring, response quality indicators
- **Conversation Context** - Maintain conversation history for better follow-up responses
- **Claude API Integration** - Full AI-powered responses with source attribution

### 🚀 Phase 2: Advanced Features - PLANNED
- Voice input/output capabilities
- File upload for user documents
- Performance optimization and caching
- Advanced UI features

### 🏆 Phase 3: Production Ready - PLANNED
- Cloud deployment (AWS)
- Monitoring and analytics
- Content expansion

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- ffmpeg (for video processing)
- Tesseract OCR (for image processing)

### 1. Clone and Setup
```bash
git clone https://github.com/jcascante/brew-master-ai.git
cd brew-master-ai
```

### 2. Start Vector Database
```bash
cd vector-db
docker compose up -d
```

### 3. Setup Data Extraction
```bash
cd data-extraction
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Setup Backend
```bash
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your API keys
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
echo "CLAUDE_MODEL=claude-3-haiku-20240307" >> .env

# Start backend
uvicorn main:app --reload
```

### 5. Setup Frontend
```bash
cd ../frontend
npm install
npm run dev
```

### 6. Test the System
```bash
# Test data extraction (if you have sample files)
cd data-extraction
python main.py --extract-audio
python main.py --transcribe-audio
python main.py --create-embeddings

# Test backend
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is beer brewing?", "top_k": 3}'

# Visit frontend
open http://localhost:5173
```

## 📚 Modules

### 🔧 Data Extraction (`data-extraction/`)
CLI tools for processing videos and presentations into searchable text.

**Features:**
- Video audio extraction and transcription with FFmpeg
- PowerPoint image extraction and OCR with Tesseract
- Vector embedding generation with multilingual models
- Batch processing with progress tracking
- **Comprehensive Logging**: File and console output with timestamps
- **Progress Monitoring**: Real-time processing status and performance metrics
- **Error Handling**: Detailed error tracking and debugging information

**Commands:**
```bash
# Complete processing pipeline
python brew_master.py process --input videos/ --output transcripts/

# Individual operations
python brew_master.py extract-audio --input videos/ --output audio/
python brew_master.py transcribe --input audio/ --output transcripts/
python brew_master.py create-embeddings --input transcripts/

# Logging options
python brew_master.py process --input videos/ --log-level DEBUG
python brew_master.py process --input videos/ --log-file custom.log

# Configuration management
python brew_master.py config --list
python brew_master.py config --show
```

**Logging & Monitoring:**
- **Default Log Location**: `./data/logs/brew_master_processing.log`
- **Production Log Location**: `/mnt/data/logs/brew_master_processing.log`
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Features**: Session tracking, timing info, progress monitoring, error details

### 🖥️ Backend (`backend/`)
FastAPI server providing RAG functionality with Claude API integration.

**Features:**
- Semantic search with Qdrant
- Claude API integration for natural responses
- Structured fallback responses when API unavailable
- Confidence scoring and response quality assessment
- Conversation context handling
- Async operations for high concurrency
- Comprehensive error handling and logging
- Health checks and monitoring

**Endpoints:**
- `GET /health` - System health check
- `POST /chat` - RAG chat endpoint

### 🎨 Frontend (`frontend/`)
React-based web interface for the chatbot.

**Features:**
- Responsive design for mobile and desktop
- Real-time chat interface with conversation context
- Export conversations as text files
- Copy individual responses with sources
- Share conversations via native sharing
- Confidence indicators and response quality badges
- Modern UI with loading states and animations

### 🗄️ Vector Database (`vector-db/`)
Docker configuration for Qdrant vector database.

**Features:**
- Local development setup
- Persistent storage
- Easy deployment to cloud

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
ANTHROPIC_API_KEY=your-claude-api-key
CLAUDE_MODEL=claude-3-haiku-20240307  # Development model
```

### Data Directories
```
data/
├── videos/                    # Input MP4 files
├── presentations/             # Input PPTX files
├── audios/                    # Extracted audio files
├── transcripts/               # Transcribed text
├── presentation_images/       # Extracted images
├── presentation_texts/        # OCR results
└── processed/                 # Moved after processing
```

## 🚀 Deployment

### Local Development
All components can run locally for development and testing.

### Production Deployment
- **Frontend**: Deploy to AWS S3 + CloudFront
- **Backend**: Containerize and deploy to AWS ECS/Lambda
- **Vector DB**: Deploy Qdrant to AWS ECS or use managed service
- **Data Processing**: Run on EC2 or use AWS Batch

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check individual module READMEs
- **Development Status**: See [CHECKPOINT.md](CHECKPOINT.md)

## 🎯 Roadmap

- [ ] Frontend API integration
- [ ] Session management and conversation history
- [ ] AWS deployment automation
- [ ] Additional data source support
- [ ] Advanced RAG techniques
- [ ] User authentication and personalization

---

**Built with ❤️ for the beer brewing community**
