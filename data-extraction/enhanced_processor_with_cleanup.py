#!/usr/bin/env python3
"""
Enhanced data processor with automatic cleanup of orphaned chunks.
Handles document deletion by removing chunks from files that no longer exist.
"""

import os
import hashlib
import logging
from typing import List, Dict, Any, Set, Tuple
from pathlib import Path
from datetime import datetime

from enhanced_processor import (
    ProcessingConfig, ChunkConfig, DataValidator, 
    TextChunker, MetadataEnricher, EnhancedDataProcessor
)
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDataProcessorWithCleanup(EnhancedDataProcessor):
    """Enhanced data processor with automatic cleanup capabilities"""
    
    def __init__(self, config: ProcessingConfig):
        super().__init__(config)
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.collection_name = "brew_master_ai"
        
    def get_existing_file_chunks(self) -> Dict[str, List[int]]:
        """Get existing chunks grouped by source file"""
        try:
            # Get all points from the collection
            points = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust based on your data size
                with_payload=True
            )[0]
            
            file_chunks = {}
            for point in points:
                source_file = point.payload.get('source_file', '')
                if source_file:
                    if source_file not in file_chunks:
                        file_chunks[source_file] = []
                    file_chunks[source_file].append(point.id)
            
            logger.info(f"Found {len(file_chunks)} files with existing chunks")
            return file_chunks
            
        except Exception as e:
            logger.warning(f"Could not retrieve existing chunks: {e}")
            return {}
    
    def get_current_files(self, data_dirs: List[str]) -> Set[str]:
        """Get set of current files in data directories"""
        current_files = set()
        
        for data_dir in data_dirs:
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.lower().endswith('.txt'):
                        # Use relative path as identifier
                        file_path = os.path.join(data_dir, filename)
                        current_files.add(file_path)
        
        logger.info(f"Found {len(current_files)} current files")
        return current_files
    
    def cleanup_orphaned_chunks(self, data_dirs: List[str]) -> Dict[str, int]:
        """Remove chunks from files that no longer exist"""
        logger.info("Starting cleanup of orphaned chunks...")
        
        # Get existing chunks grouped by file
        existing_file_chunks = self.get_existing_file_chunks()
        if not existing_file_chunks:
            logger.info("No existing chunks found, skipping cleanup")
            return {}
        
        # Get current files
        current_files = self.get_current_files(data_dirs)
        
        # Find orphaned files (exist in DB but not in filesystem)
        orphaned_files = set(existing_file_chunks.keys()) - current_files
        
        cleanup_stats = {
            'files_checked': len(existing_file_chunks),
            'files_orphaned': len(orphaned_files),
            'chunks_deleted': 0,
            'files_cleaned': []
        }
        
        if not orphaned_files:
            logger.info("No orphaned files found")
            return cleanup_stats
        
        # Delete chunks from orphaned files
        for orphaned_file in orphaned_files:
            chunk_ids = existing_file_chunks[orphaned_file]
            try:
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=qmodels.PointIdsList(
                        points=chunk_ids
                    )
                )
                cleanup_stats['chunks_deleted'] += len(chunk_ids)
                cleanup_stats['files_cleaned'].append(orphaned_file)
                logger.info(f"Deleted {len(chunk_ids)} chunks from orphaned file: {orphaned_file}")
                
            except Exception as e:
                logger.error(f"Error deleting chunks from {orphaned_file}: {e}")
        
        logger.info(f"Cleanup completed: {cleanup_stats['chunks_deleted']} chunks deleted from {len(orphaned_files)} files")
        return cleanup_stats
    
    def process_with_cleanup(self, data_dirs: List[str], content_types: List[str]) -> Dict[str, Any]:
        """Process data with automatic cleanup of orphaned chunks"""
        logger.info("Starting enhanced processing with cleanup...")
        
        # Step 1: Cleanup orphaned chunks
        cleanup_stats = self.cleanup_orphaned_chunks(data_dirs)
        
        # Step 2: Process current files
        all_chunks = []
        processing_stats = {
            'files_processed': 0,
            'chunks_created': 0,
            'chunks_validated': 0,
            'chunks_rejected': 0
        }
        
        for data_dir, content_type in zip(data_dirs, content_types):
            if os.path.exists(data_dir):
                chunks = self.process_directory(data_dir, content_type)
                all_chunks.extend(chunks)
                
                # Update stats
                stats = self.get_statistics()
                processing_stats['files_processed'] += stats['files_processed']
                processing_stats['chunks_created'] += stats['chunks_created']
                processing_stats['chunks_validated'] += stats['chunks_validated']
                processing_stats['chunks_rejected'] += stats['chunks_rejected']
        
        # Step 3: Upload to Qdrant
        if all_chunks:
            self._upload_chunks_to_qdrant(all_chunks)
        
        # Step 4: Generate summary
        summary = {
            'cleanup': cleanup_stats,
            'processing': processing_stats,
            'total_chunks_uploaded': len(all_chunks),
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def _upload_chunks_to_qdrant(self, chunks: List[Tuple[str, Dict[str, Any]]]):
        """Upload chunks to Qdrant with enhanced metadata"""
        from sentence_transformers import SentenceTransformer
        
        logger.info(f"Uploading {len(chunks)} chunks to Qdrant...")
        
        # Generate embeddings
        model = SentenceTransformer('all-MiniLM-L6-v2')
        texts = [chunk[0] for chunk in chunks]
        embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        
        # Prepare points
        points = []
        for idx, (text, metadata) in enumerate(chunks):
            # Add file path for cleanup tracking
            enhanced_metadata = metadata.copy()
            enhanced_metadata['file_path'] = metadata.get('source_path', '')
            enhanced_metadata['processing_timestamp'] = datetime.now().isoformat()
            
            points.append(qmodels.PointStruct(
                id=idx,
                vector=embeddings[idx].tolist(),
                payload=enhanced_metadata | {"text": text}
            ))
        
        # Upload to Qdrant
        try:
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully uploaded {len(points)} chunks to Qdrant")
            
        except Exception as e:
            logger.error(f"Error uploading to Qdrant: {e}")
            raise

def create_enhanced_embeddings_with_cleanup(config: ProcessingConfig | None = None):
    """Create embeddings with automatic cleanup of orphaned chunks"""
    if config is None:
        config = ProcessingConfig()
    
    processor = EnhancedDataProcessorWithCleanup(config)
    
    # Define data directories and their content types
    data_dirs = []
    content_types = []
    
    # Add transcripts if they exist
    if os.path.exists('data/transcripts'):
        data_dirs.append('data/transcripts')
        content_types.append('transcript')
    
    # Add OCR text if it exists
    if os.path.exists('data/presentation_texts'):
        data_dirs.append('data/presentation_texts')
        content_types.append('ocr')
    
    if not data_dirs:
        logger.warning("No data directories found!")
        return
    
    # Process with cleanup
    summary = processor.process_with_cleanup(data_dirs, content_types)
    
    # Print summary
    print("\n" + "="*60)
    print("ENHANCED PROCESSING WITH CLEANUP SUMMARY")
    print("="*60)
    
    print("\nCLEANUP STATISTICS:")
    print(f"  Files checked: {summary['cleanup']['files_checked']}")
    print(f"  Files orphaned: {summary['cleanup']['files_orphaned']}")
    print(f"  Chunks deleted: {summary['cleanup']['chunks_deleted']}")
    if summary['cleanup']['files_cleaned']:
        print("  Files cleaned:")
        for file in summary['cleanup']['files_cleaned']:
            print(f"    - {file}")
    
    print("\nPROCESSING STATISTICS:")
    print(f"  Files processed: {summary['processing']['files_processed']}")
    print(f"  Chunks created: {summary['processing']['chunks_created']}")
    print(f"  Chunks validated: {summary['processing']['chunks_validated']}")
    print(f"  Chunks rejected: {summary['processing']['chunks_rejected']}")
    print(f"  Total chunks uploaded: {summary['total_chunks_uploaded']}")
    
    print(f"\nTimestamp: {summary['timestamp']}")
    print("="*60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced data processing with cleanup')
    parser.add_argument('--config', type=str, default='general_brewing',
                       help='Processing configuration preset')
    parser.add_argument('--cleanup-only', action='store_true',
                       help='Only perform cleanup, no processing')
    
    args = parser.parse_args()
    
    if args.cleanup_only:
        # Only cleanup
        processor = EnhancedDataProcessorWithCleanup(ProcessingConfig())
        data_dirs = []
        if os.path.exists('data/transcripts'):
            data_dirs.append('data/transcripts')
        if os.path.exists('data/presentation_texts'):
            data_dirs.append('data/presentation_texts')
        
        cleanup_stats = processor.cleanup_orphaned_chunks(data_dirs)
        print("Cleanup completed:", cleanup_stats)
    else:
        # Full processing with cleanup
        from chunking_configs import get_config
        config = get_config(args.config)
        create_enhanced_embeddings_with_cleanup(config) 