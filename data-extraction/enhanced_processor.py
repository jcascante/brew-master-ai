import argparse
import os
import subprocess
import shutil
import re
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime
import unicodedata

# Data processing imports
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Audio and image processing
import whisper
from pptx import Presentation
import pytesseract
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
class ProcessingConfig:
    """Configuration for data processing with separate input, preprocessing, and text processing configs"""
    input_processing: InputProcessingConfig = None
    preprocessing: PreprocessingConfig = None
    text_processing: TextProcessingConfig = None
    
    def __post_init__(self):
        if self.input_processing is None:
            self.input_processing = InputProcessingConfig()
        if self.preprocessing is None:
            self.preprocessing = PreprocessingConfig()
        if self.text_processing is None:
            self.text_processing = TextProcessingConfig()
    
    # Backward compatibility properties
    @property
    def clean_text(self) -> bool:
        return self.preprocessing.clean_text
    
    @property
    def remove_stopwords(self) -> bool:
        return self.preprocessing.remove_stopwords
    
    @property
    def lemmatize(self) -> bool:
        return self.preprocessing.lemmatize
    
    @property
    def min_text_length(self) -> int:
        return self.preprocessing.min_text_length
    
    @property
    def max_text_length(self) -> int:
        return self.preprocessing.max_text_length
    
    @property
    def language(self) -> str:
        return self.preprocessing.language
    
    @property
    def chunk_config(self) -> TextProcessingConfig:
        return self.text_processing
    
    @property
    def max_chunk_size(self) -> int:
        return self.text_processing.max_chunk_size
    
    @property
    def min_chunk_size(self) -> int:
        return self.text_processing.min_chunk_size
    
    @property
    def overlap_size(self) -> int:
        return self.text_processing.overlap_size
    
    @property
    def chunk_by_sentences(self) -> bool:
        return self.text_processing.chunk_by_sentences
    
    @property
    def preserve_paragraphs(self) -> bool:
        return self.text_processing.preserve_paragraphs
    
    @property
    def max_sentences_per_chunk(self) -> int:
        return self.text_processing.max_sentences_per_chunk

class DataValidator:
    """Validates and cleans text data"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self._setup_nlp()
    
    def _setup_nlp(self):
        """Setup NLP components"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            self.stop_words = set(stopwords.words(self.config.language))
            self.lemmatizer = WordNetLemmatizer()
            
            # Try to load spaCy model for better sentence segmentation
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Using NLTK for sentence tokenization.")
                self.nlp = None
                
        except Exception as e:
            logger.error(f"Error setting up NLP components: {e}")
            self.stop_words = set()
            self.lemmatizer = None
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace and normalize unicode
        text = unicodedata.normalize('NFKC', text.strip())
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[\.\!\?]{2,}', '.', text)
        text = re.sub(r'[\,\;\:]{2,}', ',', text)
        
        return text.strip()
    
    def validate_text(self, text: str) -> Tuple[bool, str]:
        """Validate text quality and return (is_valid, reason)"""
        if not text:
            return False, "Empty text"
        
        if len(text) < self.config.min_text_length:
            return False, f"Text too short ({len(text)} chars < {self.config.min_text_length})"
        
        if len(text) > self.config.max_text_length:
            return False, f"Text too long ({len(text)} chars > {self.config.max_text_length})"
        
        # Check for meaningful content (not just whitespace/punctuation)
        words = word_tokenize(text)
        meaningful_words = [w for w in words if len(w) > 2 and w.isalpha()]
        
        if len(meaningful_words) < 5:
            return False, f"Insufficient meaningful words ({len(meaningful_words)} < 5)"
        
        # Check for repetitive content
        if len(set(meaningful_words)) / len(meaningful_words) < 0.3:
            return False, "Too much repetitive content"
        
        return True, "Valid"
    
    def preprocess_text(self, text: str) -> str:
        """Apply text preprocessing"""
        if not self.config.clean_text:
            return text
        
        text = self.clean_text(text)
        
        if self.config.remove_stopwords:
            words = word_tokenize(text)
            words = [w for w in words if w.lower() not in self.stop_words]
            text = ' '.join(words)
        
        if self.config.lemmatize and self.lemmatizer:
            words = word_tokenize(text)
            words = [self.lemmatizer.lemmatize(w) for w in words]
            text = ' '.join(words)
        
        return text

class TextChunker:
    """Advanced text chunking with multiple strategies"""
    
    def __init__(self, config: TextProcessingConfig):
        self.config = config
        self._setup_nlp()
    
    def _setup_nlp(self):
        """Setup NLP for sentence tokenization"""
        try:
            nltk.download('punkt', quiet=True)
            # Try to load spaCy for better sentence segmentation
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.nlp = None
        except Exception as e:
            logger.warning(f"Could not setup NLP: {e}")
            self.nlp = None
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """Chunk text using configured strategy"""
        if self.config.chunk_by_sentences:
            return self._chunk_by_sentences(text, metadata)
        else:
            return self._chunk_by_size(text, metadata)
    
    def _chunk_by_sentences(self, text: str, metadata: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """Chunk text by sentences with overlap"""
        if self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for i, sentence in enumerate(sentences):
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed max size
            if current_length + sentence_length > self.config.max_chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunk_metadata = self._create_chunk_metadata(metadata, len(chunks), i - len(current_chunk), i - 1)
                chunks.append((chunk_text, chunk_metadata))
                
                # Start new chunk with overlap
                if self.config.overlap_size > 0:
                    overlap_sentences = self._get_overlap_sentences(current_chunk, self.config.overlap_size)
                    current_chunk = overlap_sentences
                    current_length = sum(len(s) for s in current_chunk)
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(sentence)
            current_length += sentence_length
            
            # Check if we've reached max sentences per chunk
            if len(current_chunk) >= self.config.max_sentences_per_chunk:
                chunk_text = ' '.join(current_chunk)
                chunk_metadata = self._create_chunk_metadata(metadata, len(chunks), i - len(current_chunk) + 1, i)
                chunks.append((chunk_text, chunk_metadata))
                
                # Start new chunk with overlap
                if self.config.overlap_size > 0:
                    overlap_sentences = self._get_overlap_sentences(current_chunk, self.config.overlap_size)
                    current_chunk = overlap_sentences
                    current_length = sum(len(s) for s in current_chunk)
                else:
                    current_chunk = []
                    current_length = 0
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_metadata = self._create_chunk_metadata(metadata, len(chunks), len(sentences) - len(current_chunk), len(sentences) - 1)
            chunks.append((chunk_text, chunk_metadata))
        
        return chunks
    
    def _chunk_by_size(self, text: str, metadata: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """Chunk text by character size with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.config.max_chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending within overlap window
                overlap_start = max(start + self.config.max_chunk_size - self.config.overlap_size, start)
                for i in range(end, overlap_start, -1):
                    if text[i-1] in '.!?':
                        end = i
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_metadata = self._create_chunk_metadata(metadata, len(chunks), start, end)
                chunks.append((chunk_text, chunk_metadata))
            
            start = end - self.config.overlap_size if self.config.overlap_size > 0 else end
        
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_size: int) -> List[str]:
        """Get sentences for overlap based on character count"""
        overlap_sentences = []
        current_length = 0
        
        for sentence in reversed(sentences):
            if current_length + len(sentence) <= overlap_size:
                overlap_sentences.insert(0, sentence)
                current_length += len(sentence)
            else:
                break
        
        return overlap_sentences
    
    def _create_chunk_metadata(self, base_metadata: Dict[str, Any], chunk_index: int, 
                              start_sentence: int, end_sentence: int) -> Dict[str, Any]:
        """Create metadata for a chunk"""
        chunk_metadata = base_metadata.copy()
        chunk_metadata.update({
            'chunk_index': chunk_index,
            'start_sentence': start_sentence,
            'end_sentence': end_sentence,
            'chunk_size': end_sentence - start_sentence + 1,
            'processing_timestamp': datetime.now().isoformat()
        })
        return chunk_metadata

class MetadataEnricher:
    """Enriches metadata with additional information"""
    
    def __init__(self):
        self.content_types = {
            'transcript': 'video_transcript',
            'ocr': 'presentation_text',
            'manual': 'manual_text'
        }
    
    def enrich_metadata(self, file_path: str, content_type: str, text: str) -> Dict[str, Any]:
        """Enrich metadata with file and content information"""
        file_info = self._get_file_info(file_path)
        content_info = self._get_content_info(text, content_type)
        
        metadata = {
            'source_file': os.path.basename(file_path),
            'source_path': file_path,
            'content_type': self.content_types.get(content_type, 'unknown'),
            'file_size': file_info['size'],
            'file_modified': file_info['modified'],
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(sent_tokenize(text)),
            'content_hash': self._generate_content_hash(text),
            'processing_date': datetime.now().isoformat()
        }
        
        metadata.update(content_info)
        return metadata
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def _get_content_info(self, text: str, content_type: str) -> Dict[str, Any]:
        """Analyze content and extract information"""
        words = word_tokenize(text.lower())
        
        # Extract brewing-related keywords
        brewing_keywords = [
            'beer', 'brew', 'brewing', 'malt', 'hops', 'yeast', 'fermentation',
            'wort', 'mash', 'boil', 'lager', 'ale', 'stout', 'ipa', 'pilsner',
            'barley', 'wheat', 'rye', 'oats', 'cascade', 'citra', 'mosaic'
        ]
        
        found_keywords = [word for word in words if word in brewing_keywords]
        
        return {
            'brewing_keywords_found': len(found_keywords),
            'brewing_keywords': list(set(found_keywords)),
            'content_density': len([w for w in words if len(w) > 3]) / max(len(words), 1),
            'avg_sentence_length': len(words) / max(len(sent_tokenize(text)), 1)
        }
    
    def _generate_content_hash(self, text: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.md5(text.encode()).hexdigest()

class EnhancedDataProcessor:
    """Main data processing pipeline with enhanced features"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.validator = DataValidator(config)
        self.chunker = TextChunker(config.chunk_config)
        self.metadata_enricher = MetadataEnricher()
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'chunks_created': 0,
            'chunks_validated': 0,
            'chunks_rejected': 0,
            'total_text_length': 0
        }
    
    def process_text_file(self, file_path: str, content_type: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Process a single text file with enhanced pipeline"""
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Validate original text
            is_valid, reason = self.validator.validate_text(text)
            if not is_valid:
                logger.warning(f"File {file_path} validation failed: {reason}")
                return []
            
            # Preprocess text
            processed_text = self.validator.preprocess_text(text)
            
            # Enrich metadata
            metadata = self.metadata_enricher.enrich_metadata(file_path, content_type, processed_text)
            
            # Chunk text
            chunks = self.chunker.chunk_text(processed_text, metadata)
            
            # Validate chunks
            valid_chunks = []
            for chunk_text, chunk_metadata in chunks:
                is_valid, reason = self.validator.validate_text(chunk_text)
                if is_valid:
                    valid_chunks.append((chunk_text, chunk_metadata))
                    self.stats['chunks_validated'] += 1
                else:
                    logger.debug(f"Chunk rejected: {reason}")
                    self.stats['chunks_rejected'] += 1
            
            # Update statistics
            self.stats['files_processed'] += 1
            self.stats['chunks_created'] += len(chunks)
            self.stats['total_text_length'] += len(processed_text)
            
            logger.info(f"Created {len(valid_chunks)} valid chunks from {file_path}")
            return valid_chunks
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return []
    
    def process_directory(self, input_dir: str, content_type: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Process all text files in a directory"""
        all_chunks = []
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.txt'):
                file_path = os.path.join(input_dir, filename)
                chunks = self.process_text_file(file_path, content_type)
                all_chunks.extend(chunks)
        
        return all_chunks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.stats.copy()

def create_enhanced_embeddings(config: ProcessingConfig = None):
    """Create embeddings using the enhanced processing pipeline"""
    if config is None:
        config = ProcessingConfig()
    
    processor = EnhancedDataProcessor(config)
    
    # Process different content types
    all_chunks = []
    
    # Process transcripts
    if os.path.exists('data/transcripts'):
        logger.info("Processing video transcripts...")
        transcript_chunks = processor.process_directory('data/transcripts', 'transcript')
        all_chunks.extend(transcript_chunks)
    
    # Process OCR text
    if os.path.exists('data/presentation_texts'):
        logger.info("Processing presentation OCR text...")
        ocr_chunks = processor.process_directory('data/presentation_texts', 'ocr')
        all_chunks.extend(ocr_chunks)
    
    if not all_chunks:
        logger.warning("No text files found to process!")
        return
    
    logger.info(f"Total chunks created: {len(all_chunks)}")
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    texts = [chunk[0] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "brew_master_ai"
    
    # Create collection if not exists
    if collection_name not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(size=embeddings.shape[1], distance="Cosine")
        )
        logger.info(f"Created collection: {collection_name}")
    
    # Upload points with enhanced metadata
    points = []
    for idx, (text, metadata) in enumerate(all_chunks):
        points.append(qmodels.PointStruct(
            id=idx,
            vector=embeddings[idx].tolist(),
            payload=metadata | {"text": text}
        ))
    
    client.upsert(collection_name=collection_name, points=points)
    
    # Log statistics
    stats = processor.get_statistics()
    logger.info("Processing Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info(f"Successfully uploaded {len(points)} embeddings to Qdrant")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Enhanced Brew Master AI Data Processor')
    parser.add_argument('--create-embeddings', action='store_true', 
                       help='Create enhanced embeddings and upload to Qdrant')
    parser.add_argument('--chunk-size', type=int, default=1000,
                       help='Maximum chunk size in characters')
    parser.add_argument('--overlap', type=int, default=200,
                       help='Overlap size between chunks')
    parser.add_argument('--min-chunk', type=int, default=100,
                       help='Minimum chunk size')
    parser.add_argument('--max-sentences', type=int, default=10,
                       help='Maximum sentences per chunk')
    parser.add_argument('--clean-text', action='store_true', default=True,
                       help='Clean and normalize text')
    parser.add_argument('--remove-stopwords', action='store_true',
                       help='Remove stop words')
    parser.add_argument('--lemmatize', action='store_true',
                       help='Apply lemmatization')
    
    args = parser.parse_args()
    
    if args.create_embeddings:
        config = ProcessingConfig(
            preprocessing=PreprocessingConfig(
                clean_text=args.clean_text,
                remove_stopwords=args.remove_stopwords,
                lemmatize=args.lemmatize
            ),
            chunking=ChunkingConfig(
                max_chunk_size=args.chunk_size,
                overlap_size=args.overlap,
                min_chunk_size=args.min_chunk,
                max_sentences_per_chunk=args.max_sentences
            )
        )
        
        create_enhanced_embeddings(config) 