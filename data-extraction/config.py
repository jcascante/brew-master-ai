#!/usr/bin/env python3
"""
Unified configuration system for Brew Master AI data processing.
Combines YAML configuration, preset management, and CLI overrides.
"""

import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class InputProcessingConfig:
    """Configuration for processing raw input formats to text"""
    # Video/Audio processing
    video_quality: str = 'medium'  # low, medium, high
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    whisper_model: str = 'base'  # tiny, base, small, medium, large
    whisper_language: str = 'en'
    
    # Image/OCR processing
    ocr_language: str = 'eng'
    ocr_config: str = '--psm 6'  # Page segmentation mode
    image_preprocessing: bool = True
    image_quality_threshold: int = 70
    
    # Presentation processing
    extract_images: bool = True
    extract_text: bool = True
    image_format: str = 'png'
    image_quality: int = 90
    
    # General processing
    parallel_processing: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300


@dataclass
class PreprocessingConfig:
    """Configuration for text preprocessing and validation"""
    clean_text: bool = True
    remove_stopwords: bool = False
    lemmatize: bool = False
    min_text_length: int = 50
    max_text_length: int = 10000
    language: str = 'english'
    normalize_unicode: bool = True
    remove_special_chars: bool = False
    lowercase: bool = True
    remove_numbers: bool = False
    remove_punctuation: bool = False


@dataclass
class TextProcessingConfig:
    """Configuration for text chunking and embedding generation"""
    max_chunk_size: int = 1000
    min_chunk_size: int = 100
    overlap_size: int = 200
    chunk_by_sentences: bool = True
    preserve_paragraphs: bool = True
    max_sentences_per_chunk: int = 10
    respect_sentence_boundaries: bool = True
    smart_boundaries: bool = True
    
    # Embedding generation
    embedding_model: str = 'all-MiniLM-L6-v2'
    batch_size: int = 32
    normalize_embeddings: bool = True
    
    # Vector store settings
    collection_name: str = 'brew_master_ai'
    vector_size: int = 384
    distance_metric: str = 'cosine'


@dataclass
class ValidationConfig:
    """Configuration for data validation and quality assessment"""
    enable_validation: bool = True
    generate_reports: bool = True
    create_plots: bool = False
    report_directory: str = "data/reports/"
    min_text_length: int = 75
    max_text_length: int = 10000
    quality_threshold: float = 0.5


@dataclass
class CleanupConfig:
    """Configuration for cleanup and maintenance operations"""
    enable_cleanup: bool = True
    remove_orphaned_chunks: bool = True
    backup_before_cleanup: bool = False
    backup_directory: str = "data/backups/"
    deduplication: bool = True
    config_tracking: bool = True


@dataclass
class Config:
    """Unified configuration with all settings"""
    
    # Directories
    input_dirs: Dict[str, str] = field(default_factory=lambda: {
        'videos': 'data/input/videos/',
        'audios': 'data/audios/',
        'presentations': 'data/presentations/',
        'images': 'data/presentation_images/'
    })
    
    output_dirs: Dict[str, str] = field(default_factory=lambda: {
        'transcripts': 'data/transcripts/from_videos',
        'presentation_texts': 'data/presentation_texts/',
        'temp': 'data/temp/',
        'logs': 'data/logs/'
    })
    
    # Processing configurations
    input_processing: InputProcessingConfig = field(default_factory=InputProcessingConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    text_processing: TextProcessingConfig = field(default_factory=TextProcessingConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    cleanup: CleanupConfig = field(default_factory=CleanupConfig)
    
    # Advanced features
    smart_config: bool = True
    deduplication: bool = True
    progress_tracking: bool = True
    default_config: str = "general_brewing"
    
    # Vector database settings
    vector_db_host: str = "localhost"
    vector_db_port: int = 6333
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "data/logs/processing.log"
    
    # File type mappings
    file_extensions: Dict[str, List[str]] = field(default_factory=lambda: {
        'video': [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"],
        'audio': [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
        'presentation': [".pptx", ".ppt", ".odp"],
        'image': [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"],
        'text': [".txt", ".md", ".doc", ".docx", ".pdf"]
    })
    
    # Content type to config mapping
    content_type_configs: Dict[str, str] = field(default_factory=lambda: {
        "transcript": "video_transcript",
        "ocr": "presentation_text", 
        "manual": "general_brewing"
    })
    
    def ensure_directories(self):
        """Create all necessary directories if they don't exist"""
        all_dirs = list(self.input_dirs.values()) + list(self.output_dirs.values())
        for directory in all_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Backward compatibility properties
    @property
    def videos_dir(self) -> str:
        return self.input_dirs['videos']
    
    @property
    def audios_dir(self) -> str:
        return self.input_dirs['audios']
    
    @property
    def presentations_dir(self) -> str:
        return self.input_dirs['presentations']
    
    @property
    def images_dir(self) -> str:
        return self.input_dirs['images']
    
    @property
    def transcripts_dir(self) -> str:
        return self.output_dirs['transcripts']
    
    @property
    def presentation_texts_dir(self) -> str:
        return self.output_dirs['presentation_texts']
    
    @property
    def temp_dir(self) -> str:
        return self.output_dirs['temp']
    
    @property
    def logs_dir(self) -> str:
        return self.output_dirs['logs']


# Configuration presets
CONFIG_PRESETS = {
    # Input processing presets
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
    
    # Text processing presets
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
    
    "presentation_text": TextProcessingConfig(
        max_chunk_size=800,
        min_chunk_size=100,
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
    
    "equipment_specs": TextProcessingConfig(
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
    
    # Quality presets
    "high_quality": Config(
        input_processing=InputProcessingConfig(
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
        text_processing=TextProcessingConfig(
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
        validation=ValidationConfig(enable_validation=True, quality_threshold=0.8),
        cleanup=CleanupConfig(enable_cleanup=True, deduplication=True)
    ),
    
    "balanced": Config(
        input_processing=InputProcessingConfig(
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
        text_processing=TextProcessingConfig(
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
        validation=ValidationConfig(enable_validation=True, quality_threshold=0.6),
        cleanup=CleanupConfig(enable_cleanup=True, deduplication=True)
    ),
    
    "fast_processing": Config(
        input_processing=InputProcessingConfig(
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
        text_processing=TextProcessingConfig(
            max_chunk_size=800,
            min_chunk_size=100,
            overlap_size=100,
            chunk_by_sentences=True,
            preserve_paragraphs=False,
            max_sentences_per_chunk=8
        ),
        validation=ValidationConfig(enable_validation=False),
        cleanup=CleanupConfig(enable_cleanup=False, deduplication=False)
    )
}


class ConfigManager:
    """Configuration management with YAML + CLI overrides"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = Config()
    
    def load_config(self, cli_args: Optional[Dict[str, Any]] = None) -> Config:
        """Load configuration from YAML file and override with CLI arguments"""
        
        # Load from YAML file if it exists
        if os.path.exists(self.config_file):
            self._load_yaml_config()
        
        # Override with CLI arguments if provided
        if cli_args:
            self._override_with_cli_args(cli_args)
        
        # Ensure all directories exist
        self.config.ensure_directories()
        
        return self.config
    
    def _load_yaml_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as file:
                yaml_config = yaml.safe_load(file)
            
            if not yaml_config:
                return
            
            # Load directories
            if 'directories' in yaml_config:
                dirs = yaml_config['directories']
                self.config.input_dirs.update({
                    'videos': dirs.get('videos', self.config.input_dirs['videos']),
                    'audios': dirs.get('audios', self.config.input_dirs['audios']),
                    'presentations': dirs.get('presentations', self.config.input_dirs['presentations']),
                    'images': dirs.get('images', self.config.input_dirs['images'])
                })
                self.config.output_dirs.update({
                    'transcripts': dirs.get('transcripts', self.config.output_dirs['transcripts']),
                    'presentation_texts': dirs.get('presentation_texts', self.config.output_dirs['presentation_texts']),
                    'temp': dirs.get('temp', self.config.output_dirs['temp']),
                    'logs': dirs.get('logs', self.config.output_dirs['logs'])
                })
            
            # Load processing settings
            if 'processing' in yaml_config:
                proc = yaml_config['processing']
                self.config.default_config = proc.get('default_config', self.config.default_config)
                self.config.smart_config = proc.get('enable_smart_config', self.config.smart_config)
                self.config.deduplication = proc.get('parallel_processing', self.config.deduplication)
                self.config.input_processing.max_workers = proc.get('max_workers', self.config.input_processing.max_workers)
            
            # Load input processing settings
            if 'input_processing' in yaml_config:
                inp = yaml_config['input_processing']
                self.config.input_processing.whisper_model = inp.get('whisper_model', self.config.input_processing.whisper_model)
                self.config.input_processing.whisper_language = inp.get('whisper_language', self.config.input_processing.whisper_language)
                self.config.input_processing.ocr_language = inp.get('ocr_language', self.config.input_processing.ocr_language)
            
            # Load preprocessing settings
            if 'preprocessing' in yaml_config:
                prep = yaml_config['preprocessing']
                self.config.preprocessing.clean_text = prep.get('clean_text', self.config.preprocessing.clean_text)
                self.config.preprocessing.remove_stopwords = prep.get('remove_stopwords', self.config.preprocessing.remove_stopwords)
                self.config.preprocessing.lemmatize = prep.get('lemmatize', self.config.preprocessing.lemmatize)
                self.config.preprocessing.min_text_length = prep.get('min_text_length', self.config.preprocessing.min_text_length)
                self.config.preprocessing.max_text_length = prep.get('max_text_length', self.config.preprocessing.max_text_length)
                self.config.preprocessing.language = prep.get('language', self.config.preprocessing.language)
                self.config.preprocessing.normalize_unicode = prep.get('normalize_unicode', self.config.preprocessing.normalize_unicode)
                self.config.preprocessing.remove_special_chars = prep.get('remove_special_chars', self.config.preprocessing.remove_special_chars)
                self.config.preprocessing.lowercase = prep.get('lowercase', self.config.preprocessing.lowercase)
                self.config.preprocessing.remove_numbers = prep.get('remove_numbers', self.config.preprocessing.remove_numbers)
                self.config.preprocessing.remove_punctuation = prep.get('remove_punctuation', self.config.preprocessing.remove_punctuation)
            
            # Load text processing settings
            if 'text_processing' in yaml_config:
                txt = yaml_config['text_processing']
                self.config.text_processing.max_chunk_size = txt.get('max_chunk_size', self.config.text_processing.max_chunk_size)
                self.config.text_processing.min_chunk_size = txt.get('min_chunk_size', self.config.text_processing.min_chunk_size)
                self.config.text_processing.overlap_size = txt.get('overlap_size', self.config.text_processing.overlap_size)
                self.config.text_processing.max_sentences_per_chunk = txt.get('max_sentences_per_chunk', self.config.text_processing.max_sentences_per_chunk)
                self.config.text_processing.embedding_model = txt.get('embedding_model', self.config.text_processing.embedding_model)
                self.config.text_processing.collection_name = txt.get('collection_name', self.config.text_processing.collection_name)
            
            # Load validation settings
            if 'validation' in yaml_config:
                val = yaml_config['validation']
                self.config.validation.enable_validation = val.get('enable_validation', self.config.validation.enable_validation)
                self.config.validation.generate_reports = val.get('generate_reports', self.config.validation.generate_reports)
                self.config.validation.create_plots = val.get('create_plots', self.config.validation.create_plots)
                self.config.validation.min_text_length = val.get('min_text_length', self.config.validation.min_text_length)
                self.config.validation.max_text_length = val.get('max_text_length', self.config.validation.max_text_length)
                self.config.validation.quality_threshold = val.get('quality_threshold', self.config.validation.quality_threshold)
            
            # Load cleanup settings
            if 'cleanup' in yaml_config:
                cleanup = yaml_config['cleanup']
                self.config.cleanup.enable_cleanup = cleanup.get('enable_cleanup', self.config.cleanup.enable_cleanup)
                self.config.cleanup.remove_orphaned_chunks = cleanup.get('remove_orphaned_chunks', self.config.cleanup.remove_orphaned_chunks)
                self.config.cleanup.deduplication = cleanup.get('deduplication', self.config.cleanup.deduplication)
            
            # Load content type configs
            if 'content_type_configs' in yaml_config:
                self.config.content_type_configs.update(yaml_config['content_type_configs'])
                
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_file}: {e}")
            print("Using default configuration.")
    
    def _override_with_cli_args(self, cli_args: Dict[str, Any]):
        """Override configuration with CLI arguments"""
        # Override directories if specified
        if 'videos_dir' in cli_args and cli_args['videos_dir']:
            self.config.input_dirs['videos'] = cli_args['videos_dir']
        if 'transcripts_dir' in cli_args and cli_args['transcripts_dir']:
            self.config.output_dirs['transcripts'] = cli_args['transcripts_dir']
        if 'output_dir' in cli_args and cli_args['output_dir']:
            self.config.output_dirs['transcripts'] = cli_args['output_dir']
        
        # Override processing settings
        if 'config' in cli_args and cli_args['config']:
            self.config.default_config = cli_args['config']
        if 'max_workers' in cli_args and cli_args['max_workers']:
            self.config.input_processing.max_workers = cli_args['max_workers']
        
        # Override text processing settings
        if 'chunk_size' in cli_args and cli_args['chunk_size']:
            self.config.text_processing.max_chunk_size = cli_args['chunk_size']
        if 'overlap' in cli_args and cli_args['overlap']:
            self.config.text_processing.overlap_size = cli_args['overlap']
        if 'min_chunk' in cli_args and cli_args['min_chunk']:
            self.config.text_processing.min_chunk_size = cli_args['min_chunk']
        if 'max_sentences' in cli_args and cli_args['max_sentences']:
            self.config.text_processing.max_sentences_per_chunk = cli_args['max_sentences']
    
    def get_preset(self, name: str) -> Config:
        """Get a configuration preset"""
        if name in CONFIG_PRESETS:
            preset = CONFIG_PRESETS[name]
            if isinstance(preset, Config):
                return preset
            else:
                # If it's a sub-config, create a full config with it
                config = Config()
                if isinstance(preset, InputProcessingConfig):
                    config.input_processing = preset
                elif isinstance(preset, TextProcessingConfig):
                    config.text_processing = preset
                return config
        else:
            raise ValueError(f"Unknown preset: {name}")
    
    def list_presets(self) -> List[str]:
        """List all available presets"""
        return list(CONFIG_PRESETS.keys())
    
    def create_custom_config(self, **kwargs) -> Config:
        """Create a custom configuration with overrides"""
        config = Config()
        
        # Apply overrides
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            elif hasattr(config.text_processing, key):
                setattr(config.text_processing, key, value)
            elif hasattr(config.input_processing, key):
                setattr(config.input_processing, key, value)
            elif hasattr(config.preprocessing, key):
                setattr(config.preprocessing, key, value)
        
        return config
    
    def save_config(self, config: Config, file_path: str):
        """Save configuration to YAML file"""
        config_dict = {
            'directories': {
                **config.input_dirs,
                **config.output_dirs
            },
            'processing': {
                'default_config': config.default_config,
                'enable_smart_config': config.smart_config,
                'parallel_processing': config.deduplication,
                'max_workers': config.input_processing.max_workers
            },
            'input_processing': {
                'whisper_model': config.input_processing.whisper_model,
                'whisper_language': config.input_processing.whisper_language,
                'ocr_language': config.input_processing.ocr_language
            },
            'text_processing': {
                'max_chunk_size': config.text_processing.max_chunk_size,
                'min_chunk_size': config.text_processing.min_chunk_size,
                'overlap_size': config.text_processing.overlap_size,
                'max_sentences_per_chunk': config.text_processing.max_sentences_per_chunk,
                'embedding_model': config.text_processing.embedding_model,
                'collection_name': config.text_processing.collection_name
            },
            'preprocessing': {
                'clean_text': config.preprocessing.clean_text,
                'remove_stopwords': config.preprocessing.remove_stopwords,
                'lemmatize': config.preprocessing.lemmatize,
                'min_text_length': config.preprocessing.min_text_length,
                'max_text_length': config.preprocessing.max_text_length,
                'language': config.preprocessing.language,
                'normalize_unicode': config.preprocessing.normalize_unicode,
                'remove_special_chars': config.preprocessing.remove_special_chars,
                'lowercase': config.preprocessing.lowercase,
                'remove_numbers': config.preprocessing.remove_numbers,
                'remove_punctuation': config.preprocessing.remove_punctuation
            },
            'validation': {
                'enable_validation': config.validation.enable_validation,
                'generate_reports': config.validation.generate_reports,
                'create_plots': config.validation.create_plots,
                'min_text_length': config.validation.min_text_length,
                'max_text_length': config.validation.max_text_length,
                'quality_threshold': config.validation.quality_threshold
            },
            'cleanup': {
                'enable_cleanup': config.cleanup.enable_cleanup,
                'remove_orphaned_chunks': config.cleanup.remove_orphaned_chunks,
                'deduplication': config.cleanup.deduplication
            },
            'content_type_configs': config.content_type_configs
        }
        
        with open(file_path, 'w') as file:
            yaml.dump(config_dict, file, default_flow_style=False, indent=2)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser with configuration override options"""
    parser = argparse.ArgumentParser(description="Brew Master AI Data Processing Pipeline")
    
    # Directory overrides
    parser.add_argument('--videos-dir', help='Directory containing video files')
    parser.add_argument('--transcripts-dir', help='Directory for output transcripts')
    parser.add_argument('--output-dir', help='Output directory (alias for transcripts-dir)')
    
    # Processing overrides
    parser.add_argument('--config', help='Configuration preset to use')
    parser.add_argument('--max-workers', type=int, help='Maximum number of parallel workers')
    
    # Text processing overrides
    parser.add_argument('--chunk-size', type=int, help='Maximum chunk size')
    parser.add_argument('--overlap', type=int, help='Overlap size between chunks')
    parser.add_argument('--min-chunk', type=int, help='Minimum chunk size')
    parser.add_argument('--max-sentences', type=int, help='Maximum sentences per chunk')
    
    return parser


def get_config(preset_name: str) -> Config:
    """Get a configuration preset (backward compatibility)"""
    manager = ConfigManager()
    return manager.get_preset(preset_name)


def list_available_configs():
    """List all available configuration presets (backward compatibility)"""
    manager = ConfigManager()
    presets = manager.list_presets()
    
    print("\nAvailable Configuration Presets:")
    print("=" * 60)
    
    # Group presets by type
    input_presets = [p for p in presets if p.endswith('_input')]
    text_presets = [p for p in presets if not p.endswith('_input') and p not in ['high_quality', 'balanced', 'fast_processing']]
    quality_presets = ['high_quality', 'balanced', 'fast_processing']
    
    if input_presets:
        print("\nInput Processing Presets:")
        for preset in input_presets:
            print(f"  - {preset}")
    
    if text_presets:
        print("\nText Processing Presets:")
        for preset in text_presets:
            config = get_config(preset)
            print(f"  - {preset}: {config.text_processing.max_chunk_size} chars, {config.text_processing.overlap_size} overlap")
    
    if quality_presets:
        print("\nQuality Presets (Complete Configurations):")
        for preset in quality_presets:
            print(f"  - {preset}")


def create_custom_config(**kwargs) -> Config:
    """Create a custom configuration (backward compatibility)"""
    manager = ConfigManager()
    return manager.create_custom_config(**kwargs)


if __name__ == "__main__":
    # Test configuration system
    print("Testing configuration system...")
    
    # Test preset loading
    manager = ConfigManager()
    config = manager.get_preset("video_transcript")
    print(f"Video transcript config: {config.text_processing.max_chunk_size} chars")
    
    # Test preset listing
    list_available_configs()
    
    # Test custom config
    custom = create_custom_config(max_chunk_size=2000, overlap_size=400)
    print(f"Custom config: {custom.text_processing.max_chunk_size} chars") 