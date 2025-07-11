"""
Chunking configuration presets for different content types and use cases.
"""

from enhanced_processor import ChunkingConfig, PreprocessingConfig, ProcessingConfig

# Preprocessing configuration presets
PREPROCESSING_PRESETS = {
    # Light preprocessing - minimal changes
    "light_preprocessing": PreprocessingConfig(
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=50,
        max_text_length=15000,
        language='english',
        normalize_unicode=True,
        remove_special_chars=False,
        lowercase=True,
        remove_numbers=False,
        remove_punctuation=False
    ),
    
    # Standard preprocessing - balanced approach
    "standard_preprocessing": PreprocessingConfig(
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=75,
        max_text_length=10000,
        language='english',
        normalize_unicode=True,
        remove_special_chars=True,
        lowercase=True,
        remove_numbers=False,
        remove_punctuation=False
    ),
    
    # Aggressive preprocessing - heavy cleaning
    "aggressive_preprocessing": PreprocessingConfig(
        clean_text=True,
        remove_stopwords=True,
        lemmatize=True,
        min_text_length=100,
        max_text_length=8000,
        language='english',
        normalize_unicode=True,
        remove_special_chars=True,
        lowercase=True,
        remove_numbers=True,
        remove_punctuation=True
    ),
    
    # Technical preprocessing - preserve technical terms
    "technical_preprocessing": PreprocessingConfig(
        clean_text=True,
        remove_stopwords=False,
        lemmatize=False,
        min_text_length=100,
        max_text_length=12000,
        language='english',
        normalize_unicode=True,
        remove_special_chars=False,
        lowercase=False,  # Preserve case for technical terms
        remove_numbers=False,  # Keep measurements
        remove_punctuation=False
    )
}

# Chunking configuration presets
CHUNKING_PRESETS = {
    # For video transcripts - longer chunks to maintain context
    "video_transcript": ChunkingConfig(
        max_chunk_size=1500,
        min_chunk_size=200,
        overlap_size=300,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=15,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # For presentation text - shorter chunks for focused information
    "presentation_text": ChunkingConfig(
        max_chunk_size=800,
        min_chunk_size=150,
        overlap_size=150,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=8,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # For technical brewing content - medium chunks with technical terms preserved
    "technical_brewing": ChunkingConfig(
        max_chunk_size=1200,
        min_chunk_size=200,
        overlap_size=250,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=12,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # For general brewing content - balanced approach
    "general_brewing": ChunkingConfig(
        max_chunk_size=1000,
        min_chunk_size=150,
        overlap_size=200,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=10,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # For recipe content - preserve complete recipes
    "recipe_content": ChunkingConfig(
        max_chunk_size=2000,
        min_chunk_size=300,
        overlap_size=400,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=20,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # For FAQ content - shorter, focused chunks
    "faq_content": ChunkingConfig(
        max_chunk_size=600,
        min_chunk_size=100,
        overlap_size=100,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=6,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # For historical content - longer chunks for narrative flow
    "historical_content": ChunkingConfig(
        max_chunk_size=1800,
        min_chunk_size=250,
        overlap_size=350,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=18,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # For equipment/technical specs - preserve technical details
    "equipment_specs": ChunkingConfig(
        max_chunk_size=1000,
        min_chunk_size=200,
        overlap_size=200,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=10,
        respect_sentence_boundaries=True,
        smart_boundaries=True
    ),
    
    # Fast processing - character-based chunking
    "fast_chunking": ChunkingConfig(
        max_chunk_size=800,
        min_chunk_size=100,
        overlap_size=100,
        chunk_by_sentences=False,  # Use character-based for speed
        preserve_paragraphs=False,
        max_sentences_per_chunk=8,
        respect_sentence_boundaries=False,
        smart_boundaries=False
    )
}

# Combined configuration presets (preprocessing + chunking)
COMBINED_PRESETS = {
    # For video transcripts - light preprocessing + video chunking
    "video_transcript": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        chunking=CHUNKING_PRESETS["video_transcript"]
    ),
    
    # For presentation text - standard preprocessing + presentation chunking
    "presentation_text": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["standard_preprocessing"],
        chunking=CHUNKING_PRESETS["presentation_text"]
    ),
    
    # For technical brewing content - technical preprocessing + technical chunking
    "technical_brewing": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["technical_preprocessing"],
        chunking=CHUNKING_PRESETS["technical_brewing"]
    ),
    
    # For general brewing content - standard preprocessing + general chunking
    "general_brewing": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["standard_preprocessing"],
        chunking=CHUNKING_PRESETS["general_brewing"]
    ),
    
    # For recipe content - light preprocessing + recipe chunking
    "recipe_content": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        chunking=CHUNKING_PRESETS["recipe_content"]
    ),
    
    # For FAQ content - aggressive preprocessing + FAQ chunking
    "faq_content": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["aggressive_preprocessing"],
        chunking=CHUNKING_PRESETS["faq_content"]
    ),
    
    # For historical content - light preprocessing + historical chunking
    "historical_content": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        chunking=CHUNKING_PRESETS["historical_content"]
    ),
    
    # For equipment specs - technical preprocessing + equipment chunking
    "equipment_specs": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["technical_preprocessing"],
        chunking=CHUNKING_PRESETS["equipment_specs"]
    )
}

# Quality-based combined presets
QUALITY_PRESETS = {
    "high_quality": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        chunking=CHUNKING_PRESETS["technical_brewing"]
    ),
    
    "balanced": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["standard_preprocessing"],
        chunking=CHUNKING_PRESETS["general_brewing"]
    ),
    
    "fast_processing": ProcessingConfig(
        preprocessing=PREPROCESSING_PRESETS["aggressive_preprocessing"],
        chunking=CHUNKING_PRESETS["fast_chunking"]
    )
}

# Default configuration
DEFAULT_CONFIG = COMBINED_PRESETS["general_brewing"]

def get_config(preset_name: str) -> ProcessingConfig:
    """Get a configuration preset by name"""
    if preset_name in COMBINED_PRESETS:
        return COMBINED_PRESETS[preset_name]
    elif preset_name in QUALITY_PRESETS:
        return QUALITY_PRESETS[preset_name]
    else:
        print(f"Unknown preset: {preset_name}. Using default configuration.")
        return DEFAULT_CONFIG

def get_preprocessing_config(preset_name: str) -> PreprocessingConfig:
    """Get a preprocessing configuration preset by name"""
    if preset_name in PREPROCESSING_PRESETS:
        return PREPROCESSING_PRESETS[preset_name]
    else:
        print(f"Unknown preprocessing preset: {preset_name}. Using standard preprocessing.")
        return PREPROCESSING_PRESETS["standard_preprocessing"]

def get_chunking_config(preset_name: str) -> ChunkingConfig:
    """Get a chunking configuration preset by name"""
    if preset_name in CHUNKING_PRESETS:
        return CHUNKING_PRESETS[preset_name]
    else:
        print(f"Unknown chunking preset: {preset_name}. Using general brewing chunking.")
        return CHUNKING_PRESETS["general_brewing"]

def create_custom_config(
    # Preprocessing parameters
    clean_text: bool = True,
    remove_stopwords: bool = False,
    lemmatize: bool = False,
    min_text_length: int = 75,
    max_text_length: int = 10000,
    language: str = 'english',
    normalize_unicode: bool = True,
    remove_special_chars: bool = True,
    lowercase: bool = True,
    remove_numbers: bool = False,
    remove_punctuation: bool = False,
    # Chunking parameters
    max_chunk_size: int = 1000,
    min_chunk_size: int = 150,
    overlap_size: int = 200,
    chunk_by_sentences: bool = True,
    preserve_paragraphs: bool = True,
    max_sentences_per_chunk: int = 10,
    respect_sentence_boundaries: bool = True,
    smart_boundaries: bool = True
) -> ProcessingConfig:
    """Create a custom configuration with separate preprocessing and chunking configs"""
    
    preprocessing_config = PreprocessingConfig(
        clean_text=clean_text,
        remove_stopwords=remove_stopwords,
        lemmatize=lemmatize,
        min_text_length=min_text_length,
        max_text_length=max_text_length,
        language=language,
        normalize_unicode=normalize_unicode,
        remove_special_chars=remove_special_chars,
        lowercase=lowercase,
        remove_numbers=remove_numbers,
        remove_punctuation=remove_punctuation
    )
    
    chunking_config = ChunkingConfig(
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        overlap_size=overlap_size,
        chunk_by_sentences=chunk_by_sentences,
        preserve_paragraphs=preserve_paragraphs,
        max_sentences_per_chunk=max_sentences_per_chunk,
        respect_sentence_boundaries=respect_sentence_boundaries,
        smart_boundaries=smart_boundaries
    )
    
    return ProcessingConfig(
        preprocessing=preprocessing_config,
        chunking=chunking_config
    )

def list_available_configs():
    """List all available configuration presets"""
    print("Available Combined Presets (Preprocessing + Chunking):")
    for name in COMBINED_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Quality Presets:")
    for name in QUALITY_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Preprocessing Presets (for custom combinations):")
    for name in PREPROCESSING_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Chunking Presets (for custom combinations):")
    for name in CHUNKING_PRESETS.keys():
        print(f"  - {name}")

def create_custom_combination(preprocessing_preset: str, chunking_preset: str) -> ProcessingConfig:
    """Create a custom configuration by combining preprocessing and chunking presets"""
    preprocessing_config = get_preprocessing_config(preprocessing_preset)
    chunking_config = get_chunking_config(chunking_preset)
    
    return ProcessingConfig(
        preprocessing=preprocessing_config,
        chunking=chunking_config
    ) 