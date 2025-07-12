# 🍺 Brew Master AI - Unified Data Processing Pipeline

A comprehensive, unified data processing pipeline for Brew Master AI that transforms raw multimedia content (videos, presentations) into searchable vector embeddings for the RAG system.

## 🎯 **Overview**

This unified system consolidates all data processing functionality into a clean, maintainable architecture:

- **Single CLI** - `brew_master.py` for all operations
- **Unified Processing** - `processor.py` with all advanced features
- **Smart Configuration** - `config.py` with YAML + CLI overrides
- **Complete Pipeline** - Audio extraction → Transcription → Embeddings
- **Advanced Features** - Cleanup, deduplication, smart config selection

## 🚀 **Quick Start**

### **Complete Pipeline (Recommended)**
```bash
# Process everything from raw files to embeddings
python brew_master.py process --input videos/ --output embeddings/
```

### **Individual Operations**
```bash
# Extract audio from videos
python brew_master.py extract-audio --input videos/ --output audio/

# Transcribe audio to text
python brew_master.py transcribe --input audio/ --output transcripts/

# Create embeddings
python brew_master.py create-embeddings --input transcripts/ --config video_transcript
```

### **Configuration Management**
```bash
# List available configs
python brew_master.py config --list

# Show current config
python brew_master.py config --show

# Validate config
python brew_master.py config --validate
```

## 📁 **File Structure**

```
data-extraction/
├── 📄 brew_master.py              # Main CLI application (unified)
├── 📄 processor.py                # Core processing engine (unified)
├── 📄 config.py                   # Configuration system (unified)
├── 📄 data_validator.py           # Data validation utilities
├── 📄 config.yaml                 # Default configuration
├── 📄 requirements.txt            # Dependencies
├── 📄 README.md                   # This file
└── 📄 UNIFIED_ARCHITECTURE.md     # Architecture documentation
```

## 🔧 **Core Components**

### **1. `brew_master.py` - Main CLI Application**
Single entry point for all data processing operations with comprehensive command-line interface.

**Features:**
- Complete pipeline execution
- Individual operation commands
- Configuration management
- Data validation
- Cleanup operations
- Progress tracking and reporting

**Commands:**
```bash
# Complete pipeline
brew_master.py process --input videos/ --output embeddings/

# Individual stages
brew_master.py extract-audio --input videos/ --output audio/
brew_master.py transcribe --input audio/ --output transcripts/
brew_master.py create-embeddings --input transcripts/ --config video_transcript

# Configuration
brew_master.py config --list
brew_master.py config --show
brew_master.py config --validate

# Validation
brew_master.py validate --input transcripts/ --report quality_report.html

# Cleanup
brew_master.py cleanup --remove-orphaned
```

### **2. `processor.py` - Core Processing Engine**
Unified processing engine with all advanced features from the legacy systems.

**Classes:**
- `BrewMasterProcessor` - Main processing engine
- `DataValidator` - Text validation and cleaning
- `TextChunker` - Advanced text chunking
- `MetadataEnricher` - Rich metadata generation

**Features:**
- Audio extraction from videos
- Whisper transcription with progress tracking
- PowerPoint image extraction
- OCR text extraction
- Advanced text processing with validation
- Smart config selection
- Database cleanup and deduplication

### **3. `config.py` - Unified Configuration System**
Comprehensive configuration management with YAML files and CLI overrides.

**Features:**
- YAML configuration files
- Command-line overrides
- Configuration presets
- Smart config selection
- Validation and management

## 📊 **Configuration Presets**

### **Input Processing Presets**
- `high_quality_input` - Best quality, slower processing
- `balanced_input` - Good balance of quality and speed
- `fast_input` - Fast processing, lower quality

### **Text Processing Presets**
- `video_transcript` - Long-form video content (1500 chars, 300 overlap)
- `presentation_text` - Slide-based content (800 chars, 150 overlap)
- `general_brewing` - General text content (1000 chars, 200 overlap)
- `technical_brewing` - Technical content (1200 chars, 250 overlap)
- `recipe_content` - Recipe preservation (2000 chars, 400 overlap)
- `faq_content` - Q&A content (600 chars, 100 overlap)
- `historical_content` - Narrative content (1800 chars, 350 overlap)
- `equipment_specs` - Technical specs (1000 chars, 200 overlap)

### **Quality Presets**
- `high_quality` - Complete high-quality configuration
- `balanced` - Complete balanced configuration
- `fast_processing` - Complete fast configuration

## 🔄 **Processing Pipeline**

### **Complete Pipeline Flow**
```
Raw Files → Audio Extraction → Transcription → Text Processing → Vector DB
     ↓              ↓              ↓              ↓              ↓
Videos (.mp4) → Audio (.wav) → Transcripts (.txt) → Chunks → Embeddings
Presentations (.pptx) → Images → OCR Text (.txt) → Chunks → Embeddings
```

### **Pipeline Stages**

1. **Audio Extraction** - Extract audio from video files using ffmpeg
2. **Transcription** - Transcribe audio using Whisper AI
3. **Image Extraction** - Extract images from PowerPoint presentations
4. **OCR Processing** - Extract text from images using Tesseract
5. **Text Processing** - Validate, clean, and chunk text
6. **Embedding Creation** - Generate embeddings and upload to Qdrant
7. **Cleanup** - Remove orphaned chunks and maintain database

## ⚙️ **Configuration**

### **YAML Configuration (`config.yaml`)**
```yaml
# Input/Output directories
directories:
  videos: "data/input/videos/"
  audios: "data/audios/"
  presentations: "data/presentations/"
  transcripts: "data/transcripts/from_videos"
  presentation_texts: "data/presentation_texts/"

# Processing settings
processing:
  default_config: "general_brewing"
  enable_smart_config: true
  max_workers: 4

# Input processing
input_processing:
  whisper_model: "base"  # tiny, base, small, medium, large
  audio_sample_rate: 16000
  ocr_language: "eng"

# Text processing
text_processing:
  max_chunk_size: 1000
  min_chunk_size: 150
  overlap_size: 200
  embedding_model: "all-MiniLM-L6-v2"

# Validation
validation:
  enable_validation: true
  quality_threshold: 0.5

# Cleanup
cleanup:
  enable_cleanup: true
  remove_orphaned_chunks: true
  deduplication: true
```

### **Command-Line Overrides**
```bash
# Override any configuration setting
python brew_master.py process \
  --videos-dir /custom/videos/ \
  --chunk-size 1500 \
  --overlap 300 \
  --max-workers 8 \
  --config video_transcript
```

## 🎯 **Usage Examples**

### **Basic Usage**
```bash
# Complete pipeline with default settings
python brew_master.py process

# Complete pipeline with custom input/output
python brew_master.py process --input my_videos/ --output my_results/

# Complete pipeline with specific config
python brew_master.py process --config video_transcript
```

### **Individual Operations**
```bash
# Extract audio only
python brew_master.py extract-audio --input videos/ --output audio/

# Transcribe existing audio
python brew_master.py transcribe --input audio/ --output transcripts/

# Process presentations
python brew_master.py extract-images --input presentations/ --output images/
python brew_master.py ocr --input images/ --output ocr_text/

# Create embeddings from existing text
python brew_master.py create-embeddings --input transcripts/ --config video_transcript
```

### **Advanced Usage**
```bash
# Validate data quality
python brew_master.py validate --input transcripts/ --report quality.html --plots

# Clean up orphaned chunks
python brew_master.py cleanup --remove-orphaned

# Show configuration
python brew_master.py config --show

# List available configs
python brew_master.py config --list
```

## 🔍 **Data Validation**

The system includes comprehensive data validation:

### **Validation Features**
- Text quality assessment
- Content length validation
- Brewing keyword detection
- Repetitive content detection
- Quality scoring and reporting

### **Validation Commands**
```bash
# Validate transcripts
python brew_master.py validate --input transcripts/ --report transcript_quality.html

# Validate with visualizations
python brew_master.py validate --input transcripts/ --plots

# Validate multiple directories
python brew_master.py validate --input transcripts/ presentation_texts/ --report full_quality.html
```

## 🧹 **Database Cleanup**

### **Cleanup Features**
- Orphaned chunk detection
- Automatic cleanup of deleted files
- Config tracking and deduplication
- Backup before cleanup (optional)

### **Cleanup Commands**
```bash
# Clean up orphaned chunks
python brew_master.py cleanup --remove-orphaned

# Clean up specific directories
python brew_master.py cleanup --remove-orphaned --directories transcripts/ ocr_text/
```

## 📈 **Progress Tracking**

### **Real-Time Progress**
- File-by-file progress reporting
- Processing time estimation
- Success/failure indicators
- Detailed statistics

### **Progress Example**
```
🎵 Extracting audio from data/input/videos/ to data/audios/
[1/5] Extracting audio from video1.mp4...
✅ Audio saved to data/audios/video1.wav
[2/5] Skipping video2.mp4 (audio already exists)
...

🎤 Transcribing audio from data/audios/ to data/transcripts/from_videos
[1/3] Transcribing video1.wav (15.2 MB)...
  📊 Stats: 1250 words, 45.3 seconds (0.8 minutes)
  ⚡ Speed: 27.6 words/second
✅ Success! Transcript saved to data/transcripts/from_videos/video1.txt
```

## 🔧 **Advanced Features**

### **Smart Config Selection**
The system automatically selects the best configuration based on content type:
- **Transcripts** → `video_transcript` (larger chunks, more overlap)
- **OCR text** → `presentation_text` (smaller chunks, less overlap)
- **Manual text** → `general_brewing` (balanced approach)

### **Deduplication**
- Tracks which files were processed with which config
- Skips already processed files
- Reprocesses files when config changes
- Maintains database consistency

### **Error Handling**
- Graceful error recovery
- Continues processing on file failures
- Detailed error reporting
- Progress preservation

## 🚀 **Performance Optimization**

### **Parallel Processing**
- Configurable worker count
- Parallel audio extraction
- Batch embedding generation
- Optimized file I/O

### **Memory Management**
- Streaming text processing
- Batch chunking
- Efficient metadata handling
- Resource cleanup

### **Speed Optimizations**
- Skip already processed files
- Smart config selection
- Optimized Whisper model selection
- Efficient database operations

## 📊 **Statistics and Reporting**

### **Processing Statistics**
- Files processed, skipped, failed
- Chunks created, validated, rejected
- Processing time and speed
- Quality metrics

### **Quality Reports**
- Content quality scores
- Brewing keyword analysis
- Text length distribution
- Validation results

### **Database Statistics**
- Chunks uploaded
- Orphaned chunks removed
- Config usage tracking
- Collection metrics

## 🔧 **Installation and Setup**

### **Prerequisites**
```bash
# System dependencies
brew install ffmpeg tesseract  # macOS
# sudo apt-get install ffmpeg tesseract-ocr  # Ubuntu

# Python dependencies
pip install -r requirements.txt
```

### **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python brew_master.py config --show
```

### **Vector Database Setup**
```bash
# Start Qdrant (if not already running)
cd ../vector-db
docker compose up -d
```

## 🧪 **Testing**

### **Test the System**
```bash
# Test configuration
python brew_master.py config --validate

# Test with sample data
python brew_master.py process --input test_videos/ --config fast_processing

# Test individual components
python brew_master.py extract-audio --input test_videos/ --output test_audio/
python brew_master.py transcribe --input test_audio/ --output test_transcripts/
python brew_master.py validate --input test_transcripts/ --plots
```

## 🔄 **Migration from Legacy Systems**

### **Legacy File Mapping**
| **Legacy File** | **New Location** | **Status** |
|-----------------|------------------|------------|
| `main.py` | `brew_master.py` | ✅ **Replaced** |
| `enhanced_main.py` | `brew_master.py` | ✅ **Replaced** |
| `enhanced_processor.py` | `processor.py` | ✅ **Replaced** |
| `enhanced_processor_with_cleanup.py` | `processor.py` | ✅ **Replaced** |
| `config_loader.py` | `config.py` | ✅ **Replaced** |
| `chunking_configs.py` | `config.py` | ✅ **Replaced** |
| `run_all_pipelines.py` | `brew_master.py process` | ✅ **Replaced** |

### **Command Migration**
```bash
# Old: python main.py --extract-audio
# New: python brew_master.py extract-audio

# Old: python enhanced_main.py --transcribe-audio
# New: python brew_master.py transcribe

# Old: python enhanced_processor.py --create-embeddings
# New: python brew_master.py create-embeddings

# Old: python run_all_pipelines.py --config video_transcript
# New: python brew_master.py process --config video_transcript
```

## 🎉 **Benefits of Unified System**

### **For Users**
- ✅ **Single entry point** - One command for everything
- ✅ **Consistent interface** - Same CLI across all operations
- ✅ **Better documentation** - One comprehensive README
- ✅ **Easier installation** - Single requirements.txt

### **For Developers**
- ✅ **No duplication** - Single implementation of each feature
- ✅ **Easier maintenance** - One place to update each feature
- ✅ **Better testing** - Unified test suite
- ✅ **Cleaner codebase** - Organized, modular structure

### **For Production**
- ✅ **Reliable processing** - All advanced features in one place
- ✅ **Better error handling** - Unified error management
- ✅ **Comprehensive logging** - Consistent logging across all operations
- ✅ **Easy deployment** - Single application to deploy

## 📚 **Additional Documentation**

- **Architecture**: See `UNIFIED_ARCHITECTURE.md` for detailed design
- **Configuration**: See `config.yaml` for all available settings
- **Examples**: See command examples above for common use cases

## 🆘 **Troubleshooting**

### **Common Issues**

**Whisper Model Loading**
```bash
# If you get CUDA/GPU errors, use CPU model
python brew_master.py transcribe --config fast_processing
```

**Memory Issues**
```bash
# Reduce batch size and workers
python brew_master.py process --max-workers 2 --chunk-size 500
```

**File Permission Issues**
```bash
# Ensure write permissions
chmod -R 755 data/
```

**Vector Database Connection**
```bash
# Check if Qdrant is running
curl http://localhost:6333/collections
```

### **Getting Help**
```bash
# Show all available commands
python brew_master.py --help

# Show specific command help
python brew_master.py process --help
python brew_master.py config --help
```

---

**🍺 Brew Master AI - Unified Data Processing Pipeline**  
*Transform your brewing knowledge into intelligent searchable content!*
