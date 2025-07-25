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
    whisper_model: str = 'medium'  # tiny, base, small, medium, large - medium is good balance for Spanish
    whisper_language: str = 'es'
    
    # Whisper optimization settings for Spanish
    whisper_task: str = 'transcribe'
    whisper_temperature: float = 0.0  # Deterministic output
    whisper_fp16: bool = False  # Use float32 for better accuracy
    whisper_verbose: bool = False
    whisper_compression_ratio_threshold: float = 2.4  # Filter out non-speech
    whisper_logprob_threshold: float = -1.0  # Filter low-confidence segments
    whisper_no_speech_threshold: float = 0.6  # Filter silence
    whisper_condition_on_previous_text: bool = True  # Use context from previous segments
    whisper_initial_prompt: str = "Este es un audio sobre cerveza y técnicas de elaboración de cerveza artesanal. Incluye términos como malta, lúpulo, levadura, fermentación, macerado, hervor, y técnicas de cerveza artesanal."
    
    # Additional Whisper parameters for better quality
    whisper_best_of: int = 5  # Number of candidates to consider
    whisper_beam_size: int = 5  # Beam search size
    whisper_patience: float = 1.0  # Beam search patience
    whisper_length_penalty: float = 1.0  # Length penalty for beam search
    whisper_suppress_tokens: str = "-1"  # Suppress specific tokens
    whisper_suppress_blank: bool = True  # Suppress blank tokens
    whisper_word_timestamps: bool = True  # Get word-level timestamps
    whisper_prepend_punctuations: str = "\"'([{-"
    whisper_append_punctuations: str = "\"'.!?;:]}",
    
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
    embedding_model: str = 'paraphrase-multilingual-MiniLM-L12-v2'
    batch_size: int = 32
    normalize_embeddings: bool = True
    
    # Vector store settings
    collection_name: str = 'brew_master_ai'
    vector_size: int = 384
    distance_metric: str = 'Cosine'


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


class Config:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.environment = self._detect_environment()
        
    def _load_config(self):
        """Load configuration from YAML file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        return {}
    
    def _detect_environment(self):
        """Detect if running locally or on EC2"""
        # Check if running on EC2 (simple detection)
        if os.path.exists('/sys/hypervisor/uuid'):
            return 'production'
        return 'local'
    
    @property
    def storage_config(self):
        """Get storage configuration based on environment"""
        if self.environment == 'production':
            return {
                'local_data_dir': '/mnt/data',  # EBS mount point
                'temp_dir': '/mnt/data/temp',
                'models_dir': '/mnt/data/models',
                's3_bucket': self.config.get('s3_bucket', 'brew-master-ai-data'),
                's3_input_prefix': 'audio/input/',
                's3_output_prefix': 'transcripts/',
                's3_processed_prefix': 'audio/processed/'
            }
        else:
            return {
                'local_data_dir': './data',
                'temp_dir': './data/temp',
                'models_dir': './data/models',
                's3_bucket': self.config.get('s3_bucket', 'brew-master-ai-data'),
                's3_input_prefix': 'audio/input/',
                's3_output_prefix': 'transcripts/',
                's3_processed_prefix': 'audio/processed/'
            }
    
    @property
    def whisper_config(self):
        """Get Whisper model configuration"""
        return {
            'model_size': self.config.get('whisper_model', 'base'),
            'language': self.config.get('language', 'en'),
            'device': self.config.get('device', 'cpu')
        }
    
    def ensure_directories(self):
        """Create necessary directories"""
        storage = self.storage_config
        for dir_path in [storage['local_data_dir'], storage['temp_dir'], storage['models_dir']]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_file_paths(self, filename):
        """Get local and S3 paths for a file"""
        storage = self.storage_config
        return {
            'local_input': os.path.join(storage['temp_dir'], filename),
            'local_output': os.path.join(storage['temp_dir'], f"{filename}.txt"),
            's3_input': f"{storage['s3_input_prefix']}{filename}",
            's3_output': f"{storage['s3_output_prefix']}{filename}.txt",
            's3_processed': f"{storage['s3_processed_prefix']}{filename}"
        }

# Global config instance
config = Config()


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
        whisper_model='large',
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
        embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        batch_size=32,
        normalize_embeddings=True,
        collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
            embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
            batch_size=32,
            normalize_embeddings=True,
                    collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
            embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
            batch_size=32,
            normalize_embeddings=True,
                    collection_name='brew_master_ai',
        vector_size=384,
        distance_metric='Cosine'
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
            
            # Load vector database settings
            if 'vector_db' in yaml_config:
                vdb = yaml_config['vector_db']
                self.config.vector_db_host = vdb.get('host', self.config.vector_db_host)
                self.config.vector_db_port = vdb.get('port', self.config.vector_db_port)
                self.config.vector_db_indexing_threshold = vdb.get('indexing_threshold', self.config.vector_db_indexing_threshold)
                self.config.vector_db_memmap_threshold = vdb.get('memmap_threshold', self.config.vector_db_memmap_threshold)
            
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
    
    # Logging configuration
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level (default: INFO)')
    parser.add_argument('--log-file', help='Custom log file path (default: auto-generated)')
    
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