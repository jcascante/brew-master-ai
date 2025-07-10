# 🔧 Data Extraction Module

CLI tools for processing videos and PowerPoint presentations into searchable text for the Brew Master AI RAG system.

## 🚀 Enhanced Processing Pipeline

We now offer an **enhanced data processing pipeline** with advanced features:

- **Advanced chunking strategies** with content-type specific presets
- **Data validation and quality assessment** with brewing-specific analysis
- **Enhanced metadata enrichment** with comprehensive content information
- **Quality visualization tools** for data insights

**📖 See [ENHANCED_README.md](ENHANCED_README.md) for the complete enhanced pipeline documentation.**

## 🔄 Legacy vs Enhanced

| Feature | Legacy Pipeline | Enhanced Pipeline |
|---------|----------------|-------------------|
| Chunking | Fixed 500-char chunks | Configurable strategies |
| Validation | Basic file checks | Comprehensive quality scoring |
| Metadata | Basic file info | Rich content analysis |
| Quality | No assessment | Detailed quality reports |
| Configuration | Hard-coded | Multiple presets |
| Visualization | None | Quality plots and charts |

## 🎯 Purpose

This module transforms raw multimedia content (videos and presentations) into structured text data that can be embedded and searched by the RAG system. It handles the complete pipeline from raw files to vector database upload.

## ✨ Features

### 🎥 Video Processing
- **Audio Extraction**: Convert MP4 videos to WAV audio files
- **Transcription**: Use Whisper AI for high-quality speech-to-text
- **Multilingual Support**: Auto-detect and transcribe multiple languages
- **Batch Processing**: Handle multiple videos efficiently

### 📊 Presentation Processing
- **Image Extraction**: Extract images from PowerPoint slides
- **OCR Processing**: Convert slide images to text using Tesseract
- **Structured Output**: Maintain source file relationships

### 🧠 Vector Processing
- **Text Chunking**: Split long texts into searchable chunks
- **Embedding Generation**: Create semantic embeddings using sentence-transformers
- **Database Upload**: Store embeddings in Qdrant vector database

## 🚀 Quick Start

### Prerequisites
```bash
# Install system dependencies
brew install ffmpeg tesseract  # macOS
# sudo apt-get install ffmpeg tesseract-ocr  # Ubuntu

# Install Python dependencies
pip install -r requirements.txt
```

### Basic Usage
```bash
# 1. Extract audio from videos
python main.py --extract-audio

# 2. Transcribe audio to text
python main.py --transcribe-audio

# 3. Extract images from PowerPoint
python main.py --extract-pptx-images

# 4. Perform OCR on images
python main.py --ocr-images

# 5. Create embeddings and upload to vector database
python main.py --create-embeddings
```

## 📁 Data Flow

```
Input Files:
├── data/videos/*.mp4           # Raw video files
└── data/presentations/*.pptx   # PowerPoint presentations

Processing Pipeline:
├── data/audios/*.wav           # Extracted audio
├── data/transcripts/*.txt      # Transcribed text
├── data/presentation_images/   # Extracted slide images
├── data/presentation_texts/    # OCR results
└── data/processed/             # Moved after processing

Output:
└── Qdrant Vector Database      # Semantic embeddings
```

## 🔧 CLI Commands

### Audio Processing
```bash
python main.py --extract-audio
```
- Reads MP4 files from `data/videos/`
- Extracts audio as WAV files to `data/audios/`
- Moves processed videos to `data/processed/`

### Transcription
```bash
python main.py --transcribe-audio
```
- Transcribes WAV files using Whisper AI
- Saves transcripts as TXT files to `data/transcripts/`
- Moves processed audio to `data/processed_audios/`

### PowerPoint Processing
```bash
python main.py --extract-pptx-images
```
- Extracts images from PPTX files in `data/presentations/`
- Saves images to `data/presentation_images/`
- Moves processed presentations to `data/processed_presentations/`

### OCR Processing
```bash
python main.py --ocr-images
```
- Performs OCR on images in `data/presentation_images/`
- Saves text results to `data/presentation_texts/`
- Moves processed images to `data/processed_images/`

### Vector Database Upload
```bash
python main.py --create-embeddings
```
- Combines all text files (transcripts + OCR results)
- Chunks text into 500-character segments
- Generates embeddings using sentence-transformers
- Uploads to Qdrant collection `brew_master_ai`

## ⚙️ Configuration

### Text Chunking
- **Default chunk size**: 500 characters
- **Overlap**: None (configurable in code)
- **Chunking strategy**: Simple character-based splitting

### Embedding Model
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Distance metric**: Cosine similarity

### Vector Database
- **Collection name**: `brew_master_ai`
- **Host**: localhost:6333 (Qdrant)
- **Metadata**: Source file, chunk index

## 🧪 Testing

### Test Vector Database Queries
```bash
python test_query.py
```
Tests semantic search with sample queries and displays results.

### Sample Query
```python
query = "What is the basic process of brewing beer?"
# Returns top 3 most relevant chunks with similarity scores
```

## 🔍 Troubleshooting

### Common Issues

**ffmpeg not found:**
```bash
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

**Tesseract not found:**
```bash
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu
```

**Whisper model download:**
- First run may download the Whisper model (~1GB)
- Ensure stable internet connection

**Qdrant connection:**
- Ensure Qdrant is running: `docker compose up -d` in `vector-db/`
- Check connection at `http://localhost:6333`

### Performance Tips

1. **Batch Processing**: Process multiple files at once
2. **Model Caching**: Whisper and sentence-transformers cache models locally
3. **Memory Usage**: Large files may require more RAM
4. **GPU Acceleration**: Install CUDA for faster processing (optional)

## 📊 Output Format

### Transcript Files
```
Plain text files with transcribed speech content.
File naming: {original_video_name}.txt
```

### OCR Files
```
Plain text files with extracted text from slide images.
File naming: {original_pptx_name}_slide{number}_img{number}.txt
```

### Vector Database Records
```json
{
  "id": 0,
  "vector": [0.1, 0.2, ...],
  "payload": {
    "text": "chunk content...",
    "source_file": "transcript1.txt",
    "chunk_index": 0
  }
}
```

## 🔄 Workflow Integration

This module is designed to be run as part of the complete Brew Master AI pipeline:

1. **Data Preparation**: Place videos and presentations in input directories
2. **Processing**: Run CLI commands to extract and process content
3. **Vector Upload**: Create embeddings and upload to Qdrant
4. **RAG Integration**: Backend uses processed data for chat responses

## 📈 Future Enhancements

- [ ] Support for additional video formats
- [ ] Advanced text chunking strategies
- [ ] Parallel processing for large datasets
- [ ] Cloud storage integration
- [ ] Real-time processing capabilities
