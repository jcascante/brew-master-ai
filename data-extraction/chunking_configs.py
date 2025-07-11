"""
Configuration presets for different processing stages and content types.
"""

from enhanced_processor import InputProcessingConfig, PreprocessingConfig, TextProcessingConfig, ProcessingConfig

# Input Processing configuration presets (raw formats → text)
INPUT_PROCESSING_PRESETS = {
    # High quality video/audio processing
    "high_quality_input": InputProcessingConfig(
        video_quality='high',
        audio_sample_rate=44100,
        audio_channels=2,
        whisper_model='large',
        whisper_language='en',
        ocr_language='eng',
        ocr_config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}',
        image_preprocessing=True,
        image_quality_threshold=90,
        extract_images=True,
        extract_text=True,
        image_format='png',
        image_quality=95,
        parallel_processing=True,
        max_workers=2,
        timeout_seconds=600
    ),
    
    # Balanced input processing
    "balanced_input": InputProcessingConfig(
        video_quality='medium',
        audio_sample_rate=16000,
        audio_channels=1,
        whisper_model='base',
        whisper_language='en',
        ocr_language='eng',
        ocr_config='--psm 6',
        image_preprocessing=True,
        image_quality_threshold=70,
        extract_images=True,
        extract_text=True,
        image_format='png',
        image_quality=90,
        parallel_processing=True,
        max_workers=4,
        timeout_seconds=300
    ),
    
    # Fast input processing
    "fast_input": InputProcessingConfig(
        video_quality='low',
        audio_sample_rate=8000,
        audio_channels=1,
        whisper_model='tiny',
        whisper_language='en',
        ocr_language='eng',
        ocr_config='--psm 6',
        image_preprocessing=False,
        image_quality_threshold=50,
        extract_images=False,
        extract_text=True,
        image_format='jpeg',
        image_quality=70,
        parallel_processing=True,
        max_workers=8,
        timeout_seconds=120
    ),
    
    # Technical content input processing
    "technical_input": InputProcessingConfig(
        video_quality='high',
        audio_sample_rate=16000,
        audio_channels=1,
        whisper_model='medium',
        whisper_language='en',
        ocr_language='eng',
        ocr_config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}°F°C%pHIBUOGFG',
        image_preprocessing=True,
        image_quality_threshold=85,
        extract_images=True,
        extract_text=True,
        image_format='png',
        image_quality=95,
        parallel_processing=True,
        max_workers=4,
        timeout_seconds=400
    )
}

# Preprocessing configuration presets (text cleaning and validation)
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

# Text Processing configuration presets (text → embeddings)
TEXT_PROCESSING_PRESETS = {
    # For video transcripts - longer chunks to maintain context
    "video_transcript": TextProcessingConfig(
        max_chunk_size=1500,
        min_chunk_size=200,
        overlap_size=300,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=15,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # For presentation text - shorter chunks for focused information
    "presentation_text": TextProcessingConfig(
        max_chunk_size=800,
        min_chunk_size=150,
        overlap_size=150,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=8,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # For technical brewing content - medium chunks with technical terms preserved
    "technical_brewing": TextProcessingConfig(
        max_chunk_size=1200,
        min_chunk_size=200,
        overlap_size=250,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=12,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # For general brewing content - balanced approach
    "general_brewing": TextProcessingConfig(
        max_chunk_size=1000,
        min_chunk_size=150,
        overlap_size=200,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=10,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # For recipe content - preserve complete recipes
    "recipe_content": TextProcessingConfig(
        max_chunk_size=2000,
        min_chunk_size=300,
        overlap_size=400,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=20,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # For FAQ content - shorter, focused chunks
    "faq_content": TextProcessingConfig(
        max_chunk_size=600,
        min_chunk_size=100,
        overlap_size=100,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=6,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # For historical content - longer chunks for narrative flow
    "historical_content": TextProcessingConfig(
        max_chunk_size=1800,
        min_chunk_size=250,
        overlap_size=350,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=18,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # For equipment/technical specs - preserve technical details
    "equipment_specs": TextProcessingConfig(
        max_chunk_size=1000,
        min_chunk_size=200,
        overlap_size=200,
        chunk_by_sentences=True,
        preserve_paragraphs=True,
        max_sentences_per_chunk=10,
        respect_sentence_boundaries=True,
        smart_boundaries=True,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    ),
    
    # Fast processing - character-based chunking
    "fast_chunking": TextProcessingConfig(
        max_chunk_size=800,
        min_chunk_size=100,
        overlap_size=100,
        chunk_by_sentences=False,  # Use character-based for speed
        preserve_paragraphs=False,
        max_sentences_per_chunk=8,
        respect_sentence_boundaries=False,
        smart_boundaries=False,
        embedding_model='all-MiniLM-L6-v2',
        batch_size=64,  # Larger batch for speed
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='cosine'
    )
}

# Combined configuration presets (input + preprocessing + text processing)
COMBINED_PRESETS = {
    # For video transcripts - high quality input + light preprocessing + video chunking
    "video_transcript": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["high_quality_input"],
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["video_transcript"]
    ),
    
    # For presentation text - balanced input + standard preprocessing + presentation chunking
    "presentation_text": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["balanced_input"],
        preprocessing=PREPROCESSING_PRESETS["standard_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["presentation_text"]
    ),
    
    # For technical brewing content - technical input + technical preprocessing + technical chunking
    "technical_brewing": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["technical_input"],
        preprocessing=PREPROCESSING_PRESETS["technical_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["technical_brewing"]
    ),
    
    # For general brewing content - balanced input + standard preprocessing + general chunking
    "general_brewing": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["balanced_input"],
        preprocessing=PREPROCESSING_PRESETS["standard_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["general_brewing"]
    ),
    
    # For recipe content - high quality input + light preprocessing + recipe chunking
    "recipe_content": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["high_quality_input"],
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["recipe_content"]
    ),
    
    # For FAQ content - fast input + aggressive preprocessing + FAQ chunking
    "faq_content": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["fast_input"],
        preprocessing=PREPROCESSING_PRESETS["aggressive_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["faq_content"]
    ),
    
    # For historical content - high quality input + light preprocessing + historical chunking
    "historical_content": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["high_quality_input"],
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["historical_content"]
    ),
    
    # For equipment specs - technical input + technical preprocessing + equipment chunking
    "equipment_specs": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["technical_input"],
        preprocessing=PREPROCESSING_PRESETS["technical_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["equipment_specs"]
    )
}

# Quality-based combined presets
QUALITY_PRESETS = {
    "high_quality": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["high_quality_input"],
        preprocessing=PREPROCESSING_PRESETS["light_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["technical_brewing"]
    ),
    
    "balanced": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["balanced_input"],
        preprocessing=PREPROCESSING_PRESETS["standard_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["general_brewing"]
    ),
    
    "fast_processing": ProcessingConfig(
        input_processing=INPUT_PROCESSING_PRESETS["fast_input"],
        preprocessing=PREPROCESSING_PRESETS["aggressive_preprocessing"],
        text_processing=TEXT_PROCESSING_PRESETS["fast_chunking"]
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

def get_input_processing_config(preset_name: str) -> InputProcessingConfig:
    """Get an input processing configuration preset by name"""
    if preset_name in INPUT_PROCESSING_PRESETS:
        return INPUT_PROCESSING_PRESETS[preset_name]
    else:
        print(f"Unknown input processing preset: {preset_name}. Using balanced input processing.")
        return INPUT_PROCESSING_PRESETS["balanced_input"]

def get_preprocessing_config(preset_name: str) -> PreprocessingConfig:
    """Get a preprocessing configuration preset by name"""
    if preset_name in PREPROCESSING_PRESETS:
        return PREPROCESSING_PRESETS[preset_name]
    else:
        print(f"Unknown preprocessing preset: {preset_name}. Using standard preprocessing.")
        return PREPROCESSING_PRESETS["standard_preprocessing"]

def get_text_processing_config(preset_name: str) -> TextProcessingConfig:
    """Get a text processing configuration preset by name"""
    if preset_name in TEXT_PROCESSING_PRESETS:
        return TEXT_PROCESSING_PRESETS[preset_name]
    else:
        print(f"Unknown text processing preset: {preset_name}. Using general brewing text processing.")
        return TEXT_PROCESSING_PRESETS["general_brewing"]

def create_custom_config(
    # Input processing parameters
    video_quality: str = 'medium',
    audio_sample_rate: int = 16000,
    audio_channels: int = 1,
    whisper_model: str = 'base',
    whisper_language: str = 'en',
    ocr_language: str = 'eng',
    ocr_config: str = '--psm 6',
    image_preprocessing: bool = True,
    image_quality_threshold: int = 70,
    extract_images: bool = True,
    extract_text: bool = True,
    image_format: str = 'png',
    image_quality: int = 90,
    parallel_processing: bool = True,
    max_workers: int = 4,
    timeout_seconds: int = 300,
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
    # Text processing parameters
    max_chunk_size: int = 1000,
    min_chunk_size: int = 150,
    overlap_size: int = 200,
    chunk_by_sentences: bool = True,
    preserve_paragraphs: bool = True,
    max_sentences_per_chunk: int = 10,
    respect_sentence_boundaries: bool = True,
    smart_boundaries: bool = True,
    embedding_model: str = 'all-MiniLM-L6-v2',
    batch_size: int = 32,
    normalize_embeddings: bool = True,
    collection_name: str = 'brew_master_ai',
    vector_size: int = 384,
    distance_metric: str = 'cosine'
) -> ProcessingConfig:
    """Create a custom configuration with separate input, preprocessing, and text processing configs"""
    
    input_processing_config = InputProcessingConfig(
        video_quality=video_quality,
        audio_sample_rate=audio_sample_rate,
        audio_channels=audio_channels,
        whisper_model=whisper_model,
        whisper_language=whisper_language,
        ocr_language=ocr_language,
        ocr_config=ocr_config,
        image_preprocessing=image_preprocessing,
        image_quality_threshold=image_quality_threshold,
        extract_images=extract_images,
        extract_text=extract_text,
        image_format=image_format,
        image_quality=image_quality,
        parallel_processing=parallel_processing,
        max_workers=max_workers,
        timeout_seconds=timeout_seconds
    )
    
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
    
    text_processing_config = TextProcessingConfig(
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        overlap_size=overlap_size,
        chunk_by_sentences=chunk_by_sentences,
        preserve_paragraphs=preserve_paragraphs,
        max_sentences_per_chunk=max_sentences_per_chunk,
        respect_sentence_boundaries=respect_sentence_boundaries,
        smart_boundaries=smart_boundaries,
        embedding_model=embedding_model,
        batch_size=batch_size,
        normalize_embeddings=normalize_embeddings,
        collection_name=collection_name,
        vector_size=vector_size,
        distance_metric=distance_metric
    )
    
    return ProcessingConfig(
        input_processing=input_processing_config,
        preprocessing=preprocessing_config,
        text_processing=text_processing_config
    )

def list_available_configs():
    """List all available configuration presets"""
    print("Available Combined Presets (Input + Preprocessing + Text Processing):")
    for name in COMBINED_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Quality Presets:")
    for name in QUALITY_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Input Processing Presets (for custom combinations):")
    for name in INPUT_PROCESSING_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Preprocessing Presets (for custom combinations):")
    for name in PREPROCESSING_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nAvailable Text Processing Presets (for custom combinations):")
    for name in TEXT_PROCESSING_PRESETS.keys():
        print(f"  - {name}")

def create_custom_combination(input_preset: str, preprocessing_preset: str, text_preset: str) -> ProcessingConfig:
    """Create a custom configuration by combining input, preprocessing, and text processing presets"""
    input_config = get_input_processing_config(input_preset)
    preprocessing_config = get_preprocessing_config(preprocessing_preset)
    text_config = get_text_processing_config(text_preset)
    
    return ProcessingConfig(
        input_processing=input_config,
        preprocessing=preprocessing_config,
        text_processing=text_config
    ) 