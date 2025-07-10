"""
Chunking configuration presets for different content types and use cases.
"""

from enhanced_processor import ChunkConfig, ProcessingConfig

# Configuration for different content types
CHUNKING_PRESETS = {
    # For video transcripts - longer chunks to maintain context
    "video_transcript": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=1500,
            min_chunk_size=200,
            overlap_size=300,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=15
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=100,
        max_text_length=15000,
        language='english'
    ),
    
    # For presentation text - shorter chunks for focused information
    "presentation_text": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=800,
            min_chunk_size=150,
            overlap_size=150,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=8
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=75,
        max_text_length=8000,
        language='english'
    ),
    
    # For technical brewing content - medium chunks with technical terms preserved
    "technical_brewing": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=1200,
            min_chunk_size=200,
            overlap_size=250,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=12
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=100,
        max_text_length=12000,
        language='english'
    ),
    
    # For general brewing content - balanced approach
    "general_brewing": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=1000,
            min_chunk_size=150,
            overlap_size=200,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=10
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=75,
        max_text_length=10000,
        language='english'
    ),
    
    # For recipe content - preserve complete recipes
    "recipe_content": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=2000,
            min_chunk_size=300,
            overlap_size=400,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=20
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=150,
        max_text_length=20000,
        language='english'
    ),
    
    # For FAQ content - shorter, focused chunks
    "faq_content": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=600,
            min_chunk_size=100,
            overlap_size=100,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=6
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=50,
        max_text_length=5000,
        language='english'
    ),
    
    # For historical content - longer chunks for narrative flow
    "historical_content": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=1800,
            min_chunk_size=250,
            overlap_size=350,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=18
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=125,
        max_text_length=18000,
        language='english'
    ),
    
    # For equipment/technical specs - preserve technical details
    "equipment_specs": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=1000,
            min_chunk_size=200,
            overlap_size=200,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=10
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=100,
        max_text_length=10000,
        language='english'
    )
}

# Default configuration
DEFAULT_CONFIG = CHUNKING_PRESETS["general_brewing"]

# Configuration for different quality levels
QUALITY_PRESETS = {
    "high_quality": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=1200,
            min_chunk_size=200,
            overlap_size=250,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=12
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=100,
        max_text_length=12000,
        language='english'
    ),
    
    "balanced": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=1000,
            min_chunk_size=150,
            overlap_size=200,
            chunk_by_sentences=True,
            preserve_paragraphs=True,
            max_sentences_per_chunk=10
        ),
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=75,
        max_text_length=10000,
        language='english'
    ),
    
    "fast_processing": ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=800,
            min_chunk_size=100,
            overlap_size=100,
            chunk_by_sentences=False,  # Use character-based chunking for speed
            preserve_paragraphs=False,
            max_sentences_per_chunk=8
        ),
        clean_text=True,
        remove_stopwords=True,  # Remove stopwords for faster processing
        lemmatize=False,
        min_text_length=50,
        max_text_length=8000,
        language='english'
    )
}

def get_config(preset_name: str) -> ProcessingConfig:
    """Get a configuration preset by name"""
    if preset_name in CHUNKING_PRESETS:
        return CHUNKING_PRESETS[preset_name]
    elif preset_name in QUALITY_PRESETS:
        return QUALITY_PRESETS[preset_name]
    else:
        print(f"Unknown preset: {preset_name}. Using default configuration.")
        return DEFAULT_CONFIG

def list_available_configs():
    """List all available configuration presets"""
    print("Available Content-Type Presets:")
    for name in CHUNKING_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Quality Presets:")
    for name in QUALITY_PRESETS.keys():
        print(f"  - {name}")

def create_custom_config(
    max_chunk_size: int = 1000,
    min_chunk_size: int = 150,
    overlap_size: int = 200,
    chunk_by_sentences: bool = True,
    max_sentences_per_chunk: int = 10,
    clean_text: bool = True,
    remove_stopwords: bool = False,
    lemmatize: bool = False,
    min_text_length: int = 75,
    max_text_length: int = 10000
) -> ProcessingConfig:
    """Create a custom configuration"""
    return ProcessingConfig(
        chunk_config=ChunkConfig(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            overlap_size=overlap_size,
            chunk_by_sentences=chunk_by_sentences,
            preserve_paragraphs=True,
            max_sentences_per_chunk=max_sentences_per_chunk
        ),
        clean_text=clean_text,
        remove_stopwords=remove_stopwords,
        lemmatize=lemmatize,
        min_text_length=min_text_length,
        max_text_length=max_text_length,
        language='english'
    ) 