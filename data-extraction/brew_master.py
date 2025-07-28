#!/usr/bin/env python3
"""
Brew Master AI - Unified Data Processing CLI
Single entry point for all data processing operations with advanced features.
"""

import argparse
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import our unified modules
from config import Config, ConfigManager, create_argument_parser, list_available_configs
from processor import BrewMasterProcessor, ProcessingResult, CleanupResult
from data_validator import DataQualityAnalyzer


class BrewMasterCLI:
    """Main CLI application for Brew Master AI data processing"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_manager = ConfigManager(config_file)
        self.config = None
        self.processor = None
        self.logger = None
    
    def setup_logging(self, log_file: str = None, log_level: str = "INFO"):
        """Setup comprehensive logging to both file and console"""
        # Determine log file path
        if log_file is None:
            # Use config-based path if available, otherwise default
            if self.config and hasattr(self.config, 'storage_config'):
                log_dir = Path(self.config.storage_config.get('local_data_dir', './data')) / 'logs'
            else:
                log_dir = Path('./data/logs')
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'brew_master_processing.log'
        
        # Configure logging with both file and console handlers
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='a', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('BrewMasterAI')
        
        # Log session start
        self.logger.info('=' * 80)
        self.logger.info(f'🍺 BREW MASTER AI PROCESSING SESSION STARTED - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.logger.info('=' * 80)
        
        return self.logger
    
    def setup(self, cli_args: Dict[str, Any]):
        """Setup configuration and processor"""
        # Load configuration
        self.config = self.config_manager.load_config(cli_args)
        
        # Setup logging (after config is loaded)
        log_level = cli_args.get('log_level', 'INFO')
        log_file = cli_args.get('log_file', None)
        self.setup_logging(log_file=log_file, log_level=log_level)
        
        self.logger.info('🔧 Setting up Brew Master AI processing environment')
        self.logger.info(f'   Configuration loaded: {type(self.config).__name__}')
        
        # Create processor
        self.processor = BrewMasterProcessor(self.config)
        self.logger.info('   Processor initialized successfully')
        
        # Ensure directories exist
        self.config.ensure_directories()
        self.logger.info('   Directory structure verified')
    
    def extract_audio(self, input_dir: Optional[str] = None, output_dir: Optional[str] = None) -> ProcessingResult:
        """Extract audio from video files"""
        if self.config is None:
            raise RuntimeError("Configuration not initialized. Call setup() first.")
        if self.processor is None:
            raise RuntimeError("Processor not initialized. Call setup() first.")
            
        input_dir = input_dir or self.config.input_dirs['videos']
        output_dir = output_dir or self.config.input_dirs['audios']
        
        self.logger.info(f'🎵 STARTING AUDIO EXTRACTION')
        self.logger.info(f'   Input directory: {input_dir}')
        self.logger.info(f'   Output directory: {output_dir}')
        
        start_time = time.time()
        result = self.processor.extract_audio(input_dir, output_dir)
        processing_time = time.time() - start_time
        
        if result.success:
            self.logger.info(f'✅ Audio extraction completed successfully in {processing_time:.1f}s')
            self.logger.info(f'   Files processed: {result.files_processed}')
            if result.errors:
                self.logger.warning(f'   Errors encountered: {len(result.errors)}')
        else:
            self.logger.error(f'❌ Audio extraction failed after {processing_time:.1f}s')
            
        return result
    
    def transcribe_audio(self, input_dir: Optional[str] = None, output_dir: Optional[str] = None) -> ProcessingResult:
        """Transcribe audio files to text"""
        if self.config is None:
            raise RuntimeError("Configuration not initialized. Call setup() first.")
        if self.processor is None:
            raise RuntimeError("Processor not initialized. Call setup() first.")
            
        input_dir = input_dir or self.config.input_dirs['audios']
        output_dir = output_dir or self.config.output_dirs['transcripts']
        
        self.logger.info(f'🎤 STARTING AUDIO TRANSCRIPTION')
        self.logger.info(f'   Input directory: {input_dir}')
        self.logger.info(f'   Output directory: {output_dir}')
        
        start_time = time.time()
        result = self.processor.transcribe_audio(input_dir, output_dir)
        processing_time = time.time() - start_time
        
        if result.success:
            self.logger.info(f'✅ Audio transcription completed successfully in {processing_time:.1f}s')
            self.logger.info(f'   Files processed: {result.files_processed}')
            if result.errors:
                self.logger.warning(f'   Errors encountered: {len(result.errors)}')
        else:
            self.logger.error(f'❌ Audio transcription failed after {processing_time:.1f}s')
            
        return result
    
    def extract_images(self, input_dir: Optional[str] = None, output_dir: Optional[str] = None) -> ProcessingResult:
        """Extract images from PowerPoint presentations"""
        if self.config is None:
            raise RuntimeError("Configuration not initialized. Call setup() first.")
        if self.processor is None:
            raise RuntimeError("Processor not initialized. Call setup() first.")
            
        input_dir = input_dir or self.config.input_dirs['presentations']
        output_dir = output_dir or self.config.input_dirs['images']
        
        print(f"🖼️  Extracting images from {input_dir} to {output_dir}")
        return self.processor.extract_images(input_dir, output_dir)
    
    def ocr_images(self, input_dir: Optional[str] = None, output_dir: Optional[str] = None) -> ProcessingResult:
        """Extract text from images using OCR"""
        if self.config is None:
            raise RuntimeError("Configuration not initialized. Call setup() first.")
        if self.processor is None:
            raise RuntimeError("Processor not initialized. Call setup() first.")
            
        input_dir = input_dir or self.config.input_dirs['images']
        output_dir = output_dir or self.config.output_dirs['presentation_texts']
        
        print(f"📝 Running OCR on {input_dir} to {output_dir}")
        return self.processor.ocr_images(input_dir, output_dir)
    
    def create_embeddings(self, input_dir: str = None, config_name: str = None) -> ProcessingResult:
        """Create embeddings from text files"""
        input_dir = input_dir or self.config.output_dirs['transcripts']
        config_name = config_name or self.config.default_config
        
        print(f"🧠 Creating embeddings from {input_dir} with config: {config_name}")
        return self.processor.create_embeddings(input_dir, config_name)
    
    def validate_data(self, directory: str, output_report: str = None, create_plots: bool = False) -> Dict[str, Any]:
        """Validate and analyze data quality"""
        print(f"🔍 Validating data in: {directory}")
        
        analyzer = DataQualityAnalyzer()
        results = analyzer.analyze_directory(directory)
        
        # Generate report
        report = analyzer.generate_report(results, output_report)
        print(report)
        
        # Create visualizations if requested
        if create_plots:
            try:
                plots_dir = os.path.join(directory, "quality_plots")
                analyzer.create_visualizations(results, plots_dir)
                print(f"📊 Visualizations created in: {plots_dir}")
            except Exception as e:
                print(f"❌ Could not create visualizations: {e}")
        
        return results
    
    def cleanup_orphaned_chunks(self, data_dirs: list = None) -> CleanupResult:
        """Clean up orphaned chunks from vector database"""
        if data_dirs is None:
            data_dirs = [
                self.config.output_dirs['transcripts'],
                self.config.output_dirs['presentation_texts']
            ]
        
        print(f"🧹 Cleaning up orphaned chunks from {len(data_dirs)} directories")
        return self.processor.cleanup_orphaned_chunks(data_dirs)
    
    def process_pipeline(self, input_dir: str = None, output_dir: str = None, config_name: str = None) -> Dict[str, Any]:
        """Run complete processing pipeline"""
        self.logger.info('🚀 STARTING COMPLETE BREW MASTER AI PROCESSING PIPELINE')
        self.logger.info('=' * 80)
        
        start_time = time.time()
        results = {}
        
        # Step 1: Extract audio from videos
        self.logger.info('📹 STEP 1: Extracting audio from videos')
        audio_result = self.extract_audio(input_dir, self.config.input_dirs['audios'])
        results['audio_extraction'] = audio_result
        
        if not audio_result.success:
            self.logger.error('❌ Audio extraction failed, stopping pipeline')
            return results
        
        # Step 2: Transcribe audio to text
        self.logger.info('🎤 STEP 2: Transcribing audio to text')
        transcript_result = self.transcribe_audio(self.config.input_dirs['audios'], self.config.output_dirs['transcripts'])
        results['transcription'] = transcript_result
        
        if not transcript_result.success:
            self.logger.error('❌ Transcription failed, stopping pipeline')
            return results
        
        # Step 3: Extract images from presentations (if any)
        presentations_dir = input_dir or self.config.input_dirs['presentations']
        if os.path.exists(presentations_dir) and any(f.lower().endswith('.pptx') for f in os.listdir(presentations_dir)):
            print("\n🖼️  Step 3: Extracting images from presentations...")
            images_result = self.extract_images(presentations_dir, self.config.input_dirs['images'])
            results['image_extraction'] = images_result
            
            if images_result.success:
                print("\n📝 Step 4: Running OCR on images...")
                ocr_result = self.ocr_images(self.config.input_dirs['images'], self.config.output_dirs['presentation_texts'])
                results['ocr'] = ocr_result
        
        # Step 4: Create embeddings
        print("\n🧠 Step 5: Creating embeddings...")
        embedding_result = self.create_embeddings(self.config.output_dirs['transcripts'], config_name)
        results['embeddings'] = embedding_result
        
        # Step 5: Cleanup orphaned chunks
        if self.config.cleanup.enable_cleanup:
            print("\n🧹 Step 6: Cleaning up orphaned chunks...")
            cleanup_result = self.cleanup_orphaned_chunks()
            results['cleanup'] = cleanup_result
        
        total_time = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETED!")
        print("=" * 60)
        print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        
        for operation, result in results.items():
            if hasattr(result, 'files_processed'):
                print(f"📊 {operation}: {result.files_processed} processed, {result.files_skipped} skipped, {result.files_failed} failed")
            elif hasattr(result, 'chunks_deleted'):
                print(f"🧹 {operation}: {result.chunks_deleted} chunks deleted from {result.files_orphaned} files")
        
        return results
    
    def show_config(self):
        """Show current configuration"""
        print("⚙️  Current Configuration:")
        print("=" * 40)
        print(f"Default config: {self.config.default_config}")
        print(f"Smart config: {self.config.smart_config}")
        print(f"Deduplication: {self.config.cleanup.deduplication}")
        print(f"Whisper model: {self.config.input_processing.whisper_model}")
        print(f"Chunk size: {self.config.text_processing.max_chunk_size}")
        print(f"Overlap size: {self.config.text_processing.overlap_size}")
        print(f"Vector DB: {self.config.vector_db_host}:{self.config.vector_db_port}")
        print(f"Collection: {self.config.text_processing.collection_name}")
        
        print("\n📁 Directories:")
        for name, path in self.config.input_dirs.items():
            print(f"  {name}: {path}")
        for name, path in self.config.output_dirs.items():
            print(f"  {name}: {path}")
    
    def list_configs(self):
        """List available configuration presets"""
        list_available_configs()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Brew Master AI - Unified Data Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete pipeline
  brew_master.py process --input videos/ --output embeddings/
  
  # Individual operations
  brew_master.py extract-audio --input videos/ --output audio/
  brew_master.py transcribe --input audio/ --output transcripts/
  brew_master.py create-embeddings --input transcripts/ --config video_transcript
  
  # Configuration
  brew_master.py config --list
  brew_master.py config --show
  
  # Validation
  brew_master.py validate --input transcripts/ --report quality_report.html
  
  # Cleanup
  brew_master.py cleanup --remove-orphaned
        """
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command (complete pipeline)
    process_parser = subparsers.add_parser('process', help='Run complete processing pipeline')
    process_parser.add_argument('--input', help='Input directory containing videos/presentations')
    process_parser.add_argument('--output', help='Output directory for results')
    process_parser.add_argument('--config', help='Configuration preset to use')
    process_parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                               default='INFO', help='Set logging level (default: INFO)')
    process_parser.add_argument('--log-file', help='Custom log file path (default: auto-generated)')
    
    # Extract audio command
    audio_parser = subparsers.add_parser('extract-audio', help='Extract audio from video files')
    audio_parser.add_argument('--input', help='Directory containing video files')
    audio_parser.add_argument('--output', help='Output directory for audio files')
    
    # Transcribe command
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcribe audio files to text')
    transcribe_parser.add_argument('--input', help='Directory containing audio files')
    transcribe_parser.add_argument('--output', help='Output directory for transcripts')
    
    # Extract images command
    images_parser = subparsers.add_parser('extract-images', help='Extract images from PowerPoint presentations')
    images_parser.add_argument('--input', help='Directory containing PowerPoint files')
    images_parser.add_argument('--output', help='Output directory for images')
    
    # OCR command
    ocr_parser = subparsers.add_parser('ocr', help='Extract text from images using OCR')
    ocr_parser.add_argument('--input', help='Directory containing images')
    ocr_parser.add_argument('--output', help='Output directory for OCR text')
    
    # Create embeddings command
    embeddings_parser = subparsers.add_parser('create-embeddings', help='Create embeddings from text files')
    embeddings_parser.add_argument('--input', help='Directory containing text files')
    embeddings_parser.add_argument('--config', help='Configuration preset to use')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data quality')
    validate_parser.add_argument('--input', required=True, help='Directory to validate')
    validate_parser.add_argument('--report', help='Output file for quality report')
    validate_parser.add_argument('--plots', action='store_true', help='Create quality visualization plots')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up orphaned chunks')
    cleanup_parser.add_argument('--remove-orphaned', action='store_true', help='Remove orphaned chunks from database')
    cleanup_parser.add_argument('--directories', nargs='+', help='Directories to check for orphaned chunks')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--list', action='store_true', help='List available configuration presets')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--validate', action='store_true', help='Validate current configuration')
    
    # Add configuration override arguments to all parsers
    for subparser in [process_parser, audio_parser, transcribe_parser, images_parser, 
                     ocr_parser, embeddings_parser, validate_parser, cleanup_parser]:
        subparser.add_argument('--config-file', help='YAML configuration file to load (default: config.yaml)')
        subparser.add_argument('--videos-dir', help='Directory containing video files')
        subparser.add_argument('--transcripts-dir', help='Directory for output transcripts')
        subparser.add_argument('--output-dir', help='Output directory (alias for transcripts-dir)')
        subparser.add_argument('--max-workers', type=int, help='Maximum number of parallel workers')
        subparser.add_argument('--chunk-size', type=int, help='Maximum chunk size')
        subparser.add_argument('--overlap', type=int, help='Overlap size between chunks')
        subparser.add_argument('--min-chunk', type=int, help='Minimum chunk size')
        subparser.add_argument('--max-sentences', type=int, help='Maximum sentences per chunk')
    
    args = parser.parse_args()
    
    # Convert args to dict for config loading
    cli_args = {k: v for k, v in vars(args).items() if v is not None and k != 'command'}
    
    # Create CLI instance with custom config file if specified
    config_file = cli_args.get('config_file', 'config.yaml')
    cli = BrewMasterCLI(config_file)
    
    # Handle config commands first
    if args.command == 'config':
        if args.list:
            cli.list_configs()
        elif args.show:
            cli.setup(cli_args)
            cli.show_config()
        elif args.validate:
            cli.setup(cli_args)
            print("✅ Configuration is valid")
        else:
            config_parser.print_help()
        return
    
    # Setup configuration and processor
    cli.setup(cli_args)
    
    # Execute commands
    if args.command == 'process':
        cli.process_pipeline(args.input, args.output, args.config)
    
    elif args.command == 'extract-audio':
        cli.extract_audio(args.input, args.output)
    
    elif args.command == 'transcribe':
        cli.transcribe_audio(args.input, args.output)
    
    elif args.command == 'extract-images':
        cli.extract_images(args.input, args.output)
    
    elif args.command == 'ocr':
        cli.ocr_images(args.input, args.output)
    
    elif args.command == 'create-embeddings':
        cli.create_embeddings(args.input, args.config)
    
    elif args.command == 'validate':
        cli.validate_data(args.input, args.report, args.plots)
    
    elif args.command == 'cleanup':
        if args.remove_orphaned:
            cli.cleanup_orphaned_chunks(args.directories)
        else:
            cleanup_parser.print_help()
    
    else:
        # No command specified, show help
        parser.print_help()


if __name__ == '__main__':
    main() 