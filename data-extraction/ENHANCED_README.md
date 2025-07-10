# 🚀 Enhanced Data Processing Pipeline

This enhanced data processing pipeline provides advanced features for chunking strategies, data validation, metadata enrichment, and quality assessment for the Brew Master AI system.

## ✨ New Features

### 🧩 Advanced Chunking Strategies
- **Sentence-based chunking** with configurable overlap
- **Content-type specific presets** (video transcripts, presentations, recipes, etc.)
- **Quality-based configurations** (high quality, balanced, fast processing)
- **Custom chunking parameters** for fine-tuning

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
└── Cleanup reporting               # Detailed statistics

chunking_configs.py       # Configuration presets
├── Content-type presets  # Video, presentation, recipe, etc.
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

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd data-extraction
pip install -r requirements.txt

# Optional: Install spaCy model for better sentence segmentation
python -m spacy download en_core_web_sm
```

### 2. List Available Configurations

```bash
python enhanced_main.py --list-configs
```

### 3. Process Data with Enhanced Pipeline

```bash
# Extract and transcribe with validation
python enhanced_main.py --extract-audio
python enhanced_main.py --transcribe-audio --validate

# Create embeddings with specific configuration
python enhanced_main.py --create-embeddings --config technical_brewing

# Create embeddings with automatic cleanup
python enhanced_processor_with_cleanup.py --config technical_brewing

# Run only cleanup (no processing)
python enhanced_processor_with_cleanup.py --cleanup-only

# Validate existing data
python enhanced_main.py --validate data/transcripts --report quality_report.txt --plots
```

## 📋 Configuration Presets

### Content-Type Presets

| Preset | Max Chunk | Overlap | Use Case |
|--------|-----------|---------|----------|
| `video_transcript` | 1500 | 300 | Long-form video content |
| `presentation_text` | 800 | 150 | Slide-based information |
| `technical_brewing` | 1200 | 250 | Technical brewing content |
| `recipe_content` | 2000 | 400 | Complete recipe preservation |
| `faq_content` | 600 | 100 | Q&A format content |
| `historical_content` | 1800 | 350 | Narrative historical content |
| `equipment_specs` | 1000 | 200 | Technical specifications |

### Quality Presets

| Preset | Description | Speed | Quality |
|--------|-------------|-------|---------|
| `high_quality` | Best quality, slower processing | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| `balanced` | Good balance of speed and quality | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| `fast_processing` | Fastest processing, basic quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🔧 Advanced Usage

### Custom Chunking Configuration

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