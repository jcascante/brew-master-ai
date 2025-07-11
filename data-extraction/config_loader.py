#!/usr/bin/env python3
"""
Configuration loader for Brew Master AI data processing pipeline.
Loads settings from config.yaml and allows command-line overrides.
"""

import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class that holds all pipeline settings"""
    
    # Directories
    videos_dir: str = "data/videos/"
    audios_dir: str = "data/audios/"
    presentations_dir: str = "data/presentations/"
    images_dir: str = "data/presentation_images/"
    transcripts_dir: str = "data/transcripts/"
    presentation_texts_dir: str = "data/presentation_texts/"
    temp_dir: str = "data/temp/"
    logs_dir: str = "data/logs/"
    
    # Processing settings
    default_config: str = "general_brewing"
    enable_smart_config: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    extraction_timeout: int = 300
    transcription_timeout: int = 600
    embedding_timeout: int = 300
    
    # Input processing settings
    video_quality: str = "medium"
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    whisper_model: str = "base"
    whisper_language: str = "en"
    ocr_language: str = "eng"
    ocr_config: str = "--psm 6"
    image_preprocessing: bool = True
    image_quality_threshold: int = 70
    extract_images: bool = True
    extract_text: bool = True
    image_format: str = "png"
    image_quality: int = 90
    
    # Text processing settings
    max_chunk_size: int = 1000
    min_chunk_size: int = 150
    overlap_size: int = 200
    chunk_by_sentences: bool = True
    preserve_paragraphs: bool = True
    max_sentences_per_chunk: int = 10
    embedding_model: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    normalize_embeddings: bool = True
    collection_name: str = "brew_master_ai"
    vector_size: int = 384
    distance_metric: str = "cosine"
    
    # Preprocessing settings
    clean_text: bool = True
    remove_stopwords: bool = False
    lemmatize: bool = False
    min_text_length: int = 75
    max_text_length: int = 10000
    language: str = "english"
    normalize_unicode: bool = True
    remove_special_chars: bool = True
    lowercase: bool = True
    remove_numbers: bool = False
    remove_punctuation: bool = False
    
    # Vector DB settings
    vector_db_host: str = "localhost"
    vector_db_port: int = 6333
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "data/logs/processing.log"
    max_log_file_size: str = "10MB"
    log_backup_count: int = 5
    
    # Validation settings
    enable_validation: bool = True
    generate_reports: bool = True
    create_plots: bool = False
    report_directory: str = "data/reports/"
    
    # Cleanup settings
    enable_cleanup: bool = True
    remove_orphaned_chunks: bool = True
    backup_before_cleanup: bool = False
    backup_directory: str = "data/backups/"
    
    # File type mappings
    video_extensions: list = field(default_factory=lambda: [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"])
    audio_extensions: list = field(default_factory=lambda: [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"])
    presentation_extensions: list = field(default_factory=lambda: [".pptx", ".ppt", ".odp"])
    image_extensions: list = field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"])
    text_extensions: list = field(default_factory=lambda: [".txt", ".md", ".doc", ".docx", ".pdf"])
    
    # Content type to config mapping
    content_type_configs: Dict[str, str] = field(default_factory=lambda: {
        "transcript": "video_transcript",
        "ocr": "presentation_text", 
        "manual": "general_brewing"
    })
    
    def ensure_directories(self):
        """Create all necessary directories if they don't exist"""
        directories = [
            self.videos_dir, self.audios_dir, self.presentations_dir,
            self.images_dir, self.transcripts_dir, self.presentation_texts_dir,
            self.temp_dir, self.logs_dir, self.report_directory, self.backup_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_input_directories(self) -> Dict[str, str]:
        """Get all input directories"""
        return {
            "videos": self.videos_dir,
            "audios": self.audios_dir,
            "presentations": self.presentations_dir,
            "images": self.images_dir
        }
    
    def get_output_directories(self) -> Dict[str, str]:
        """Get all output directories"""
        return {
            "transcripts": self.transcripts_dir,
            "presentation_texts": self.presentation_texts_dir
        }
    
    def get_file_extension_mapping(self) -> Dict[str, list]:
        """Get file extension mappings"""
        return {
            "video": self.video_extensions,
            "audio": self.audio_extensions,
            "presentation": self.presentation_extensions,
            "image": self.image_extensions,
            "text": self.text_extensions
        }


class ConfigLoader:
    """Loads and manages configuration from YAML file and command-line arguments"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = Config()
    
    def load_config(self, args: Optional[argparse.Namespace] = None) -> Config:
        """Load configuration from YAML file and override with command-line arguments"""
        
        # Load from YAML file if it exists
        if os.path.exists(self.config_file):
            self._load_yaml_config()
        
        # Override with command-line arguments if provided
        if args:
            self._override_with_args(args)
        
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
                self.config.videos_dir = dirs.get('videos', self.config.videos_dir)
                self.config.audios_dir = dirs.get('audios', self.config.audios_dir)
                self.config.presentations_dir = dirs.get('presentations', self.config.presentations_dir)
                self.config.images_dir = dirs.get('images', self.config.images_dir)
                self.config.transcripts_dir = dirs.get('transcripts', self.config.transcripts_dir)
                self.config.presentation_texts_dir = dirs.get('presentation_texts', self.config.presentation_texts_dir)
                self.config.temp_dir = dirs.get('temp', self.config.temp_dir)
                self.config.logs_dir = dirs.get('logs', self.config.logs_dir)
            
            # Load processing settings
            if 'processing' in yaml_config:
                proc = yaml_config['processing']
                self.config.default_config = proc.get('default_config', self.config.default_config)
                self.config.enable_smart_config = proc.get('enable_smart_config', self.config.enable_smart_config)
                self.config.parallel_processing = proc.get('parallel_processing', self.config.parallel_processing)
                self.config.max_workers = proc.get('max_workers', self.config.max_workers)
                self.config.extraction_timeout = proc.get('extraction_timeout', self.config.extraction_timeout)
                self.config.transcription_timeout = proc.get('transcription_timeout', self.config.transcription_timeout)
                self.config.embedding_timeout = proc.get('embedding_timeout', self.config.embedding_timeout)
            
            # Load input processing settings
            if 'input_processing' in yaml_config:
                inp = yaml_config['input_processing']
                self.config.video_quality = inp.get('video_quality', self.config.video_quality)
                self.config.audio_sample_rate = inp.get('audio_sample_rate', self.config.audio_sample_rate)
                self.config.audio_channels = inp.get('audio_channels', self.config.audio_channels)
                self.config.whisper_model = inp.get('whisper_model', self.config.whisper_model)
                self.config.whisper_language = inp.get('whisper_language', self.config.whisper_language)
                self.config.ocr_language = inp.get('ocr_language', self.config.ocr_language)
                self.config.ocr_config = inp.get('ocr_config', self.config.ocr_config)
                self.config.image_preprocessing = inp.get('image_preprocessing', self.config.image_preprocessing)
                self.config.image_quality_threshold = inp.get('image_quality_threshold', self.config.image_quality_threshold)
                self.config.extract_images = inp.get('extract_images', self.config.extract_images)
                self.config.extract_text = inp.get('extract_text', self.config.extract_text)
                self.config.image_format = inp.get('image_format', self.config.image_format)
                self.config.image_quality = inp.get('image_quality', self.config.image_quality)
            
            # Load text processing settings
            if 'text_processing' in yaml_config:
                txt = yaml_config['text_processing']
                self.config.max_chunk_size = txt.get('max_chunk_size', self.config.max_chunk_size)
                self.config.min_chunk_size = txt.get('min_chunk_size', self.config.min_chunk_size)
                self.config.overlap_size = txt.get('overlap_size', self.config.overlap_size)
                self.config.chunk_by_sentences = txt.get('chunk_by_sentences', self.config.chunk_by_sentences)
                self.config.preserve_paragraphs = txt.get('preserve_paragraphs', self.config.preserve_paragraphs)
                self.config.max_sentences_per_chunk = txt.get('max_sentences_per_chunk', self.config.max_sentences_per_chunk)
                self.config.embedding_model = txt.get('embedding_model', self.config.embedding_model)
                self.config.batch_size = txt.get('batch_size', self.config.batch_size)
                self.config.normalize_embeddings = txt.get('normalize_embeddings', self.config.normalize_embeddings)
                self.config.collection_name = txt.get('collection_name', self.config.collection_name)
                self.config.vector_size = txt.get('vector_size', self.config.vector_size)
                self.config.distance_metric = txt.get('distance_metric', self.config.distance_metric)
            
            # Load preprocessing settings
            if 'preprocessing' in yaml_config:
                prep = yaml_config['preprocessing']
                self.config.clean_text = prep.get('clean_text', self.config.clean_text)
                self.config.remove_stopwords = prep.get('remove_stopwords', self.config.remove_stopwords)
                self.config.lemmatize = prep.get('lemmatize', self.config.lemmatize)
                self.config.min_text_length = prep.get('min_text_length', self.config.min_text_length)
                self.config.max_text_length = prep.get('max_text_length', self.config.max_text_length)
                self.config.language = prep.get('language', self.config.language)
                self.config.normalize_unicode = prep.get('normalize_unicode', self.config.normalize_unicode)
                self.config.remove_special_chars = prep.get('remove_special_chars', self.config.remove_special_chars)
                self.config.lowercase = prep.get('lowercase', self.config.lowercase)
                self.config.remove_numbers = prep.get('remove_numbers', self.config.remove_numbers)
                self.config.remove_punctuation = prep.get('remove_punctuation', self.config.remove_punctuation)
            
            # Load vector DB settings
            if 'vector_db' in yaml_config:
                vdb = yaml_config['vector_db']
                self.config.vector_db_host = vdb.get('host', self.config.vector_db_host)
                self.config.vector_db_port = vdb.get('port', self.config.vector_db_port)
                self.config.collection_name = vdb.get('collection_name', self.config.collection_name)
                self.config.vector_size = vdb.get('vector_size', self.config.vector_size)
                self.config.distance_metric = vdb.get('distance_metric', self.config.distance_metric)
            
            # Load logging settings
            if 'logging' in yaml_config:
                log = yaml_config['logging']
                self.config.log_level = log.get('level', self.config.log_level)
                self.config.log_format = log.get('format', self.config.log_format)
                self.config.log_file = log.get('file', self.config.log_file)
                self.config.max_log_file_size = log.get('max_file_size', self.config.max_log_file_size)
                self.config.log_backup_count = log.get('backup_count', self.config.log_backup_count)
            
            # Load validation settings
            if 'validation' in yaml_config:
                val = yaml_config['validation']
                self.config.enable_validation = val.get('enable_validation', self.config.enable_validation)
                self.config.generate_reports = val.get('generate_reports', self.config.generate_reports)
                self.config.create_plots = val.get('create_plots', self.config.create_plots)
                self.config.report_directory = val.get('report_directory', self.config.report_directory)
            
            # Load cleanup settings
            if 'cleanup' in yaml_config:
                cleanup = yaml_config['cleanup']
                self.config.enable_cleanup = cleanup.get('enable_cleanup', self.config.enable_cleanup)
                self.config.remove_orphaned_chunks = cleanup.get('remove_orphaned_chunks', self.config.remove_orphaned_chunks)
                self.config.backup_before_cleanup = cleanup.get('backup_before_cleanup', self.config.backup_before_cleanup)
                self.config.backup_directory = cleanup.get('backup_directory', self.config.backup_directory)
            
            # Load file type mappings
            if 'file_type_mapping' in yaml_config:
                ftm = yaml_config['file_type_mapping']
                self.config.video_extensions = ftm.get('video_extensions', self.config.video_extensions)
                self.config.audio_extensions = ftm.get('audio_extensions', self.config.audio_extensions)
                self.config.presentation_extensions = ftm.get('presentation_extensions', self.config.presentation_extensions)
                self.config.image_extensions = ftm.get('image_extensions', self.config.image_extensions)
                self.config.text_extensions = ftm.get('text_extensions', self.config.text_extensions)
            
            # Load content type configs
            if 'content_type_configs' in yaml_config:
                self.config.content_type_configs.update(yaml_config['content_type_configs'])
                
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_file}: {e}")
            print("Using default configuration.")
    
    def _override_with_args(self, args: argparse.Namespace):
        """Override configuration with command-line arguments"""
        # Override directories if specified
        if hasattr(args, 'videos_dir') and args.videos_dir:
            self.config.videos_dir = args.videos_dir
        if hasattr(args, 'transcripts_dir') and args.transcripts_dir:
            self.config.transcripts_dir = args.transcripts_dir
        if hasattr(args, 'output_dir') and args.output_dir:
            self.config.transcripts_dir = args.output_dir
        
        # Override processing settings
        if hasattr(args, 'config') and args.config:
            self.config.default_config = args.config
        if hasattr(args, 'max_workers') and args.max_workers:
            self.config.max_workers = args.max_workers
        
        # Override text processing settings
        if hasattr(args, 'chunk_size') and args.chunk_size:
            self.config.max_chunk_size = args.chunk_size
        if hasattr(args, 'overlap') and args.overlap:
            self.config.overlap_size = args.overlap
        if hasattr(args, 'min_chunk') and args.min_chunk:
            self.config.min_chunk_size = args.min_chunk
        if hasattr(args, 'max_sentences') and args.max_sentences:
            self.config.max_sentences_per_chunk = args.max_sentences


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


# Global config instance
_global_config = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _global_config
    if _global_config is None:
        loader = ConfigLoader()
        _global_config = loader.load_config()
    return _global_config

def set_config(config: Config):
    """Set the global configuration instance"""
    global _global_config
    _global_config = config 