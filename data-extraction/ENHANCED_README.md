# 🚀 Enhanced Data Processing Pipeline

This enhanced data processing pipeline provides advanced features for chunking strategies, data validation, metadata enrichment, and quality assessment for the Brew Master AI system.

## ✨ New Features

### 🧩 Advanced Chunking Strategies
- **Sentence-based chunking** with configurable overlap
- **Content-type specific presets** (video transcripts, presentations, recipes, etc.)
- **Quality-based configurations** (high quality, balanced, fast processing)
- **Custom chunking parameters** for fine-tuning
- **Separate preprocessing and chunking configs** for maximum flexibility

### 🔍 Data Validation & Quality Assessment
- **Comprehensive text validation** with quality scoring
- **Brewing-specific content analysis** with keyword detection
- **Quality issue identification** and reporting
- **Visualization tools** for data quality insights

### 📊 Enhanced Metadata
- **Rich metadata enrichment** with file and content information
- **Content hash generation** for deduplication
- **Brewing keyword analysis** and categorization
- **Processing timestamps** and quality metrics

### 🧹 Data Cleaning & Preprocessing
- **Text normalization** and cleaning
- **Unicode normalization** and special character handling
- **Configurable preprocessing** (stopword removal, lemmatization)
- **Quality filtering** with minimum/maximum thresholds

### 🗑️ Automatic Cleanup
- **Orphaned chunk detection** when source files are deleted
- **Automatic cleanup** of chunks from removed files
- **File tracking** using file paths as unique identifiers
- **Cleanup reporting** with detailed statistics

### 🧠 Smart Config Selection
- **Automatic config selection** based on content type
- **File-based deduplication** to prevent duplicate processing
- **Config tracking** in metadata for transparency
- **Manual override** available when needed

## 🏗️ Architecture

### Core Components

```
enhanced_processor.py      # Main processing pipeline
├── DataValidator         # Text validation and cleaning
├── TextChunker          # Advanced chunking strategies
├── MetadataEnricher     # Metadata enhancement
└── EnhancedDataProcessor # Main orchestrator

enhanced_processor_with_cleanup.py  # Cleanup-enabled processor
├── EnhancedDataProcessorWithCleanup # Automatic cleanup capabilities
├── Orphaned chunk detection        # File-based tracking
├── Smart config selection          # Content-type based config selection
├── File deduplication              # Prevents duplicate processing
└── Cleanup reporting               # Detailed statistics

chunking_configs.py       # Configuration presets
├── Preprocessing presets # Light, standard, aggressive, technical
├── Chunking presets      # Video, presentation, recipe, etc.
├── Combined presets      # Preprocessing + chunking combinations
├── Quality presets       # High, balanced, fast
└── Custom config builder # Fine-tuned configurations

data_validator.py         # Quality assessment tools
├── DataQualityAnalyzer   # Comprehensive analysis
├── Quality scoring       # Content quality metrics
└── Visualization tools   # Quality plots and reports

enhanced_main.py          # Enhanced CLI interface
```

## 📂 Input Folders

The enhanced pipeline expects input data in the following folders:

| Content Type | Input Folder               | Description                                 |
|--------------|---------------------------|---------------------------------------------|
| transcript   | data/transcripts/         | Video/audio transcriptions (from Whisper)   |
| ocr          | data/presentation_texts/  | OCR text from presentation images (Tesseract)|
| (raw video)  | data/videos/              | Raw video files (for extraction step only)  |
| (audio)      | data/audios/              | Extracted audio files (for extraction only) |
| (presentation)| data/presentations/      | PowerPoint files (for extraction only)      |
| (images)     | data/presentation_images/ | Extracted images (for OCR step only)        |

> **Note:** Only `data/transcripts/` and `data/presentation_texts/` are used as input for the enhanced embedding and cleanup pipeline. The other folders are used in earlier extraction steps.

All enhanced processing configs (e.g., `general_brewing`, `technical_brewing`, `video_transcript`, `presentation_text`, etc.) use:
- `data/transcripts/` for transcript content
- `data/presentation_texts/` for OCR content

The config determines **how** the text is chunked and processed, but **not** the input folder location.

## 🏗️ Three-Stage Configuration System

The enhanced pipeline now uses a **three-stage configuration system** for maximum flexibility and clarity:

### 1. Input Processing Config (`InputProcessingConfig`)
- Handles raw input files (videos, audio, images, presentations)
- Controls extraction, transcription, and OCR settings
- Example: Whisper model, audio sample rate, OCR language, image preprocessing

### 2. Preprocessing Config (`PreprocessingConfig`)
- Handles text cleaning, normalization, and validation
- Example: Remove stopwords, lemmatize, case normalization, min/max text length

### 3. Text Processing Config (`TextProcessingConfig`)
- Handles chunking, embedding generation, and vector store loading
- Example: Chunk size, overlap, embedding model, vector DB settings

### 🔄 How It Works
- **InputProcessingConfig**: Raw file → Text (transcription, OCR, etc.)
- **PreprocessingConfig**: Text cleaning/normalization
- **TextProcessingConfig**: Text → Embeddings (chunking, embedding, vector store)

### 🧩 Example: Creating a Custom Three-Stage Config
```python
from chunking_configs import create_custom_combination

# Choose presets for each stage
config = create_custom_combination(
    input_preset='technical_input',
    preprocessing_preset='technical_preprocessing',
    text_preset='technical_brewing'
)

# Use in your pipeline:
# config.input_processing, config.preprocessing, config.text_processing
```

### 🛠️ Available Presets

| Stage                | Presets (examples)                |
|----------------------|-----------------------------------|
| Input Processing     | high_quality_input, balanced_input, fast_input, technical_input |
| Preprocessing        | light_preprocessing, standard_preprocessing, aggressive_preprocessing, technical_preprocessing |
| Text Processing      | video_transcript, presentation_text, technical_brewing, general_brewing, recipe_content, faq_content, historical_content, equipment_specs, fast_chunking |

### 🚀 Practical Scenarios
- **High Quality Video Pipeline**: `high_quality_input` + `light_preprocessing` + `video_transcript`
- **Technical Brewing Pipeline**: `technical_input` + `technical_preprocessing` + `technical_brewing`
- **Fast OCR Pipeline**: `fast_input` + `aggressive_preprocessing` + `fast_chunking`
- **Balanced General Pipeline**: `balanced_input` + `standard_preprocessing` + `general_brewing`

See `test_three_stage_configs.py` for a demonstration script.

## 🧑‍💻 Advanced Usage Examples

### 1. Dynamic Config Selection Based on File Type

```python
from chunking_configs import create_custom_combination

def select_config_for_file(file_path):
    if file_path.endswith('.mp4') or file_path.endswith('.wav'):
        # Video/audio: high quality input, light preprocessing, video transcript chunking
        return create_custom_combination('high_quality_input', 'light_preprocessing', 'video_transcript')
    elif file_path.endswith('.pptx') or file_path.endswith('.jpg'):
        # Presentations/images: balanced input, standard preprocessing, presentation chunking
        return create_custom_combination('balanced_input', 'standard_preprocessing', 'presentation_text')
    elif file_path.endswith('.txt'):
        # Technical text: skip input, use technical preprocessing and chunking
        return create_custom_combination('technical_input', 'technical_preprocessing', 'technical_brewing')
    else:
        # Fallback: fast processing
        return create_custom_combination('fast_input', 'aggressive_preprocessing', 'fast_chunking')

# Example usage
for file in ['lecture.mp4', 'slides.pptx', 'manual.txt']:
    config = select_config_for_file(file)
    print(f"Config for {file}:")
    print("  Input:", config.input_processing)
    print("  Preprocessing:", config.preprocessing)
    print("  Text Processing:", config.text_processing)
```

---

### 2. Customizing Only One Stage

```python
from chunking_configs import (
    get_input_processing_config,
    get_preprocessing_config,
    get_text_processing_config,
    ProcessingConfig
)

# Use a custom text processing config, but default input and preprocessing
custom_text_config = get_text_processing_config('recipe_content')
config = ProcessingConfig(
    input_processing=get_input_processing_config('balanced_input'),
    preprocessing=get_preprocessing_config('standard_preprocessing'),
    text_processing=custom_text_config
)
```

---

### 3. Fully Custom Configuration (No Presets)

```python
from chunking_configs import create_custom_config

config = create_custom_config(
    # Input processing
    video_quality='high',
    audio_sample_rate=48000,
    whisper_model='large',
    # Preprocessing
    clean_text=True,
    remove_stopwords=True,
    lemmatize=True,
    min_text_length=200,
    # Text processing
    max_chunk_size=1800,
    overlap_size=400,
    embedding_model='all-mpnet-base-v2',
    collection_name='custom_brew_collection'
)
```

---

### 4. Integrating with a Real Pipeline

Suppose you have a pipeline function that expects a `ProcessingConfig`:

```python
def run_pipeline(config, input_files):
    # 1. Use config.input_processing for extraction/transcription/OCR
    # 2. Use config.preprocessing for text cleaning
    # 3. Use config.text_processing for chunking, embedding, and vector DB
    pass

# Choose a config for a technical brewing batch
config = create_custom_combination('technical_input', 'technical_preprocessing', 'technical_brewing')
run_pipeline(config, input_files=['brew_talk.mp4', 'brew_notes.txt'])
```

---

### 5. Batch Processing with Different Configs

You can process different batches with different configs in the same script:

```python
batches = [
    ('video_batch', ['vid1.mp4', 'vid2.mp4'], 'high_quality_input', 'light_preprocessing', 'video_transcript'),
    ('ocr_batch', ['slide1.jpg', 'slide2.jpg'], 'fast_input', 'aggressive_preprocessing', 'presentation_text'),
]

for batch_name, files, input_p, prep_p, text_p in batches:
    config = create_custom_combination(input_p, prep_p, text_p)
    print(f"Processing {batch_name} with config: {config}")
    run_pipeline(config, files)
```

## 📋 Configuration Options

The enhanced pipeline offers separate preprocessing and chunking configurations for maximum flexibility:

### Preprocessing Presets

| Preset | Description | Text Cleaning | Stopwords | Lemmatize | Case | Numbers |
|--------|-------------|---------------|-----------|-----------|------|---------|
| `light_preprocessing` | Minimal changes | ✅ | ❌ | ❌ | Lower | Keep |
| `standard_preprocessing` | Balanced cleaning | ✅ | ❌ | ❌ | Lower | Keep |
| `aggressive_preprocessing` | Heavy cleaning | ✅ | ✅ | ✅ | Lower | Remove |
| `technical_preprocessing` | Preserve technical terms | ✅ | ❌ | ❌ | Preserve | Keep |

### Chunking Presets

| Preset | Max Chunk | Overlap | Use Case |
|--------|-----------|---------|----------|
| `video_transcript` | 1500 | 300 | Long-form video content |
| `presentation_text` | 800 | 150 | Slide-based information |
| `technical_brewing` | 1200 | 250 | Technical brewing content |
| `recipe_content` | 2000 | 400 | Complete recipe preservation |
| `faq_content` | 600 | 100 | Q&A format content |
| `historical_content` | 1800 | 350 | Narrative historical content |
| `equipment_specs` | 1000 | 200 | Technical specifications |
| `fast_chunking` | 800 | 100 | Character-based, fast processing |

### Combined Presets (Preprocessing + Chunking)

| Preset | Preprocessing | Chunking | Use Case |
|--------|---------------|----------|----------|
| `video_transcript` | light_preprocessing | video_transcript | Video content |
| `presentation_text` | standard_preprocessing | presentation_text | Slide content |
| `technical_brewing` | technical_preprocessing | technical_brewing | Technical content |
| `general_brewing` | standard_preprocessing | general_brewing | General content |
| `recipe_content` | light_preprocessing | recipe_content | Recipe content |
| `faq_content` | aggressive_preprocessing | faq_content | FAQ content |
| `historical_content` | light_preprocessing | historical_content | Historical content |
| `equipment_specs` | technical_preprocessing | equipment_specs | Equipment specs |

### Quality Presets

| Preset | Description | Speed | Quality |
|--------|-------------|-------|---------|
| `high_quality` | Best quality, slower processing | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| `balanced` | Good balance of speed and quality | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| `fast_processing` | Fastest processing, basic quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🔧 Advanced Usage

### Custom Configuration Combinations

```python
# Create custom preprocessing + chunking combination
from chunking_configs import create_custom_combination
config = create_custom_combination('technical_preprocessing', 'video_transcript')
create_enhanced_embeddings_with_cleanup(config)

# Create fully custom configuration
from chunking_configs import create_custom_config
config = create_custom_config(
    # Preprocessing settings
    clean_text=True, remove_stopwords=False, lemmatize=False,
    min_text_length=100, max_text_length=15000,
    normalize_unicode=True, remove_special_chars=False,
    lowercase=False, remove_numbers=False, remove_punctuation=False,
    # Chunking settings
    max_chunk_size=1500, min_chunk_size=200, overlap_size=300,
    chunk_by_sentences=True, preserve_paragraphs=True,
    max_sentences_per_chunk=15, respect_sentence_boundaries=True,
    smart_boundaries=True
)
```

### Custom Chunking Configuration (Legacy)

```bash
# Create embeddings with custom parameters
python enhanced_main.py --create-embeddings \
  --chunk-size 1200 \
  --overlap 250 \
  --min-chunk 200 \
  --max-sentences 12
```

### Data Quality Analysis

```bash
# Analyze transcripts with detailed report
python enhanced_main.py --validate data/transcripts \
  --report transcript_quality.txt \
  --plots

# Analyze presentation text
python enhanced_main.py --validate data/presentation_texts \
  --report presentation_quality.txt
```

### Batch Processing with Validation

```bash
# Complete pipeline with validation at each step
python enhanced_main.py --extract-audio
python enhanced_main.py --transcribe-audio --validate
python enhanced_main.py --extract-pptx-images
python enhanced_main.py --ocr-images --validate
python enhanced_main.py --create-embeddings --config balanced

## 🗑️ Automatic Cleanup Functionality

The enhanced pipeline now includes automatic cleanup capabilities that handle document deletion by removing orphaned chunks from the vector database.

### How Cleanup Works

1. **File Tracking**: The system tracks which files are currently in the data directories
2. **Database Scan**: It scans the Qdrant database for existing chunks
3. **Orphan Detection**: Identifies chunks from files that no longer exist
4. **Automatic Removal**: Deletes orphaned chunks while preserving unchanged data
5. **Reporting**: Provides detailed cleanup statistics

### Cleanup Benefits

- **Automatic Maintenance**: No manual cleanup required
- **Data Consistency**: Ensures database reflects current file state
- **Storage Efficiency**: Removes unnecessary orphaned data
- **Process Simplification**: No need to move files to processed folders

### Usage Examples

```bash
# Process with automatic cleanup (recommended)
python enhanced_processor_with_cleanup.py --config general_brewing

# Run only cleanup without processing
python enhanced_processor_with_cleanup.py --cleanup-only

# Full pipeline with cleanup
python run_all_pipelines.py --config general_brewing
```

### Cleanup Report Example

```
============================================================
ENHANCED PROCESSING WITH CLEANUP SUMMARY
============================================================

CLEANUP STATISTICS:
  Files checked: 15
  Files orphaned: 3
  Chunks deleted: 24
  Files cleaned:
    - data/transcripts/old_file1.txt
    - data/transcripts/old_file2.txt
    - data/presentation_texts/outdated_slide.txt

PROCESSING STATISTICS:
  Files processed: 12
  Chunks created: 156
  Chunks validated: 152
  Chunks rejected: 4
  Total chunks uploaded: 152

Timestamp: 2024-01-15T10:30:45.123456
============================================================
```

## 🎯 Benefits of Separate Configurations

The new separate preprocessing and chunking configuration system provides maximum flexibility:

### Key Benefits
- **Mix and Match**: Combine any preprocessing strategy with any chunking strategy
- **Content Optimization**: Use light preprocessing for technical content with detailed chunking
- **Speed Control**: Fast preprocessing with detailed chunking (or vice versa)
- **Fine-grained Control**: Precise control over every aspect of the pipeline
- **Future-proof**: Easy to add new preprocessing or chunking strategies independently

### Practical Examples
- **Technical Documents**: `technical_preprocessing` + `technical_brewing` (preserve case/numbers + medium chunks)
- **Video Transcripts**: `light_preprocessing` + `video_transcript` (minimal changes + long chunks)
- **Fast Processing**: `aggressive_preprocessing` + `fast_chunking` (heavy cleaning + character-based)
- **High Quality**: `light_preprocessing` + `technical_brewing` (preserve original + detailed chunking)

## 🧠 Smart Config Selection

The enhanced pipeline now includes intelligent config selection that automatically chooses the optimal chunking strategy for each content type.

### How Smart Config Selection Works

1. **Content Type Detection**: System identifies content type based on input folder
2. **Automatic Config Mapping**: 
   - `transcript` content → `video_transcript` config (longer chunks, more overlap)
   - `ocr` content → `presentation_text` config (shorter chunks, focused)
   - `manual` content → `general_brewing` config (balanced approach)
3. **File Deduplication**: Tracks which files were processed with which config
4. **Skip Logic**: Skips files already processed with the same config
5. **Manual Override**: Allows manual config selection when needed

### Smart Config Mapping

| Content Type | Auto-Selected Config | Chunk Size | Overlap | Use Case |
|--------------|---------------------|------------|---------|----------|
| transcript   | video_transcript    | 1500       | 300     | Long-form video content |
| ocr          | presentation_text   | 800        | 150     | Slide-based information |
| manual       | general_brewing     | 1000       | 200     | General text content |

### Benefits

- **✅ No Duplicate Processing**: Files are only processed once per config
- **✅ Optimal Chunking**: Each content type gets the best chunking strategy
- **✅ Automatic Operation**: No manual config selection needed
- **✅ Transparency**: Config used is tracked in metadata
- **✅ Flexibility**: Manual override available when needed

### Usage Examples

```bash
# Auto-config selection (recommended)
python enhanced_processor_with_cleanup.py
# Transcripts → video_transcript config
# OCR → presentation_text config

# Manual override
python enhanced_processor_with_cleanup.py --config technical_brewing
# All content uses technical_brewing config

# Full pipeline with smart config
python run_all_pipelines.py
# Complete pipeline with automatic config selection
```

### Processing Report Example

```
PROCESSING STATISTICS:
  Files processed: 8
  Files skipped (already processed): 3
  Chunks created: 24
  Chunks validated: 22
  Chunks rejected: 2
  Total chunks uploaded: 22

Configs used:
  - video_transcript: 5 files (transcripts)
  - presentation_text: 3 files (OCR)
```
```

## 📊 Quality Metrics

### Validation Criteria

- **Text Length**: Minimum 50 chars, maximum 10,000 chars
- **Meaningful Content**: At least 5 meaningful words
- **Content Diversity**: Less than 70% repetitive content
- **Brewing Relevance**: Brewing keyword detection
- **Sentence Structure**: Proper sentence count and structure

### Quality Scoring

Quality scores (0.0 - 1.0) are based on:
- **Content Validity** (30%): Passes validation criteria
- **Content Length** (20%): Appropriate word count
- **Brewing Relevance** (30%): Brewing keyword density
- **Sentence Structure** (10%): Proper sentence count
- **Issue Penalties** (10%): Deductions for quality issues

### Brewing Keywords

The system detects brewing-specific keywords across categories:

- **Process**: mash, boil, ferment, condition, bottle, keg
- **Ingredients**: malt, hops, yeast, water, barley, wheat, rye
- **Equipment**: kettle, mash tun, fermenter, bottles, kegs
- **Styles**: lager, ale, stout, ipa, pilsner, porter, wheat
- **Measurements**: gravity, abv, ibu, srm, ph, temperature
- **Techniques**: dry hopping, cold crashing, lagering, sparging

## 📈 Quality Reports

### Report Sections

1. **Summary Statistics**: File counts, validity rates, text metrics
2. **Quality Issues**: Breakdown of identified problems
3. **Brewing Keywords**: Frequency analysis of brewing terms
4. **Individual File Analysis**: Per-file quality scores and issues

### Visualization Outputs

- **Quality Score Distribution**: Histogram of file quality scores
- **Brewing Keywords Frequency**: Bar chart of top brewing terms
- **Quality Issues Breakdown**: Pie chart of issue types

## 🔍 Data Validation Examples

### Valid Content Example
```
✅ transcript_brewing_basics.txt: Score 0.85, 1,250 words, 15 brewing keywords
```

### Invalid Content Example
```
❌ transcript_noise.txt: Score 0.15, 25 words, 0 brewing keywords
Issues: too_short, low_brewing_content, insufficient_sentences
```

## 🛠️ Troubleshooting

### Common Issues

1. **spaCy Model Not Found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Matplotlib/Seaborn Not Available**
   - Install optional dependencies: `pip install matplotlib seaborn`
   - Or run without visualization: omit `--plots` flag

3. **Low Quality Scores**
   - Check content relevance to brewing
   - Ensure sufficient text length
   - Verify proper sentence structure

4. **Chunking Issues**
   - Adjust chunk size for content type
   - Increase overlap for better context
   - Use content-specific presets

### Performance Optimization

- Use `fast_processing` preset for large datasets
- Enable stopword removal for faster processing
- Use character-based chunking instead of sentence-based
- Process in smaller batches for memory management

## 📚 API Reference

### EnhancedDataProcessor

```python
from enhanced_processor import EnhancedDataProcessor, ProcessingConfig

# Create processor with custom config
config = ProcessingConfig(
    chunk_config=ChunkConfig(max_chunk_size=1000, overlap_size=200),
    clean_text=True,
    min_text_length=100
)

processor = EnhancedDataProcessor(config)
chunks = processor.process_directory('data/transcripts', 'transcript')
```

### DataQualityAnalyzer

```python
from data_validator import DataQualityAnalyzer

analyzer = DataQualityAnalyzer()
results = analyzer.analyze_directory('data/transcripts')
report = analyzer.generate_report(results, 'quality_report.txt')
analyzer.create_visualizations(results, 'plots/')
```

### Configuration Management

```python
from chunking_configs import get_config, create_custom_config

# Use preset configuration
config = get_config('technical_brewing')

# Create custom configuration
config = create_custom_config(
    max_chunk_size=1200,
    overlap_size=250,
    chunk_by_sentences=True
)
```

## 🎯 Best Practices

### Chunking Strategy Selection

1. **Video Transcripts**: Use `video_transcript` preset for narrative content
2. **Presentations**: Use `presentation_text` preset for slide-based content
3. **Recipes**: Use `recipe_content` preset to preserve complete recipes
4. **Technical Content**: Use `technical_brewing` preset for detailed information
5. **FAQs**: Use `faq_content` preset for question-answer format

### Quality Assurance

1. **Always validate** after transcription and OCR
2. **Review quality reports** before creating embeddings
3. **Use appropriate presets** for content type
4. **Monitor brewing keyword density** for relevance
5. **Check for duplicate content** using content hashes

### Performance Considerations

1. **Batch processing** for large datasets
2. **Memory management** for large files
3. **Parallel processing** where possible
4. **Caching** for repeated operations
5. **Incremental updates** for new content

## 🔄 Migration from Legacy Pipeline

### Step-by-Step Migration

1. **Backup existing data**
   ```bash
   cp -r data/ data_backup/
   ```

2. **Validate existing content**
   ```bash
   python enhanced_main.py --validate data/transcripts
   ```

3. **Recreate embeddings with enhanced pipeline**
   ```bash
   python enhanced_main.py --create-embeddings --config balanced
   ```

4. **Compare quality metrics**
   - Review quality reports
   - Check brewing keyword coverage
   - Verify chunk quality

### Compatibility

- **Backward compatible** with existing data structure
- **Enhanced metadata** adds new fields without breaking existing ones
- **Gradual migration** possible with mixed old/new embeddings
- **Quality validation** helps identify problematic legacy content

## 📞 Support

For issues and questions:
1. Check quality reports for data issues
2. Review configuration presets for optimization
3. Use validation tools to diagnose problems
4. Consult brewing keyword analysis for content relevance

---

**Enhanced Data Processing Pipeline** - Making Brew Master AI smarter with better data! 🍺✨ 