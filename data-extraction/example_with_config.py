#!/usr/bin/env python3
"""
Example script showing how to use the configuration system
to process videos with custom settings and directories.
"""

import argparse
import sys
from pathlib import Path
from config_loader import ConfigLoader, create_argument_parser, get_config


def main():
    """Main function demonstrating configuration usage"""
    
    # Create argument parser with config override options
    parser = create_argument_parser()
    
    # Add your own arguments
    parser.add_argument('--extract-audio', action='store_true', help='Extract audio from videos')
    parser.add_argument('--transcribe', action='store_true', help='Transcribe audio to text')
    parser.add_argument('--create-embeddings', action='store_true', help='Create embeddings and update vector DB')
    parser.add_argument('--full-pipeline', action='store_true', help='Run complete pipeline')
    
    args = parser.parse_args()
    
    # Load configuration (YAML file + command-line overrides)
    loader = ConfigLoader()
    config = loader.load_config(args)
    
    print("=== Brew Master AI - Configuration Example ===")
    print(f"Configuration loaded from: {loader.config_file}")
    print()
    
    # Display current configuration
    print("📁 Directory Configuration:")
    print(f"  Videos: {config.videos_dir}")
    print(f"  Audios: {config.audios_dir}")
    print(f"  Transcripts: {config.transcripts_dir}")
    print(f"  Logs: {config.logs_dir}")
    print()
    
    print("⚙️ Processing Configuration:")
    print(f"  Default Config: {config.default_config}")
    print(f"  Smart Config: {config.enable_smart_config}")
    print(f"  Max Workers: {config.max_workers}")
    print()
    
    print("🎥 Input Processing Settings:")
    print(f"  Video Quality: {config.video_quality}")
    print(f"  Whisper Model: {config.whisper_model}")
    print(f"  Audio Sample Rate: {config.audio_sample_rate}")
    print()
    
    print("📝 Text Processing Settings:")
    print(f"  Max Chunk Size: {config.max_chunk_size}")
    print(f"  Overlap Size: {config.overlap_size}")
    print(f"  Embedding Model: {config.embedding_model}")
    print()
    
    # Check if input directories exist and have files
    print("🔍 Checking Input Directories:")
    for dir_name, dir_path in config.get_input_directories().items():
        path = Path(dir_path)
        if path.exists():
            files = list(path.glob('*'))
            print(f"  {dir_name}: {len(files)} files found")
        else:
            print(f"  {dir_name}: Directory does not exist")
    print()
    
    # Example pipeline commands based on configuration
    if args.full_pipeline or (args.extract_audio and args.transcribe and args.create_embeddings):
        print("🚀 Running Complete Pipeline:")
        print(f"  # Extract audio from videos in {config.videos_dir}")
        print("  python enhanced_main.py --extract-audio")
        print()
        print(f"  # Transcribe audio to {config.transcripts_dir}")
        print("  python enhanced_main.py --transcribe-audio --validate")
        print()
        print(f"  # Create embeddings with {config.default_config} config")
        print(f"  python enhanced_processor_with_cleanup.py --config {config.default_config}")
        print()
        
    elif args.extract_audio:
        print("🎵 Audio Extraction Command:")
        print("  python enhanced_main.py --extract-audio")
        print()
        
    elif args.transcribe:
        print("📝 Transcription Command:")
        print("  python enhanced_main.py --transcribe-audio --validate")
        print()
        
    elif args.create_embeddings:
        print("🧠 Embedding Creation Command:")
        print(f"  python enhanced_processor_with_cleanup.py --config {config.default_config}")
        print()
    
    else:
        print("💡 Usage Examples:")
        print("  # Run complete pipeline")
        print("  python example_with_config.py --full-pipeline")
        print()
        print("  # Custom directories")
        print("  python example_with_config.py --videos-dir /path/to/videos --transcripts-dir /path/to/output --full-pipeline")
        print()
        print("  # Custom processing settings")
        print("  python example_with_config.py --config technical_brewing --chunk-size 1500 --overlap 300 --full-pipeline")
        print()
        print("  # Individual steps")
        print("  python example_with_config.py --extract-audio")
        print("  python example_with_config.py --transcribe")
        print("  python example_with_config.py --create-embeddings")
        print()


if __name__ == "__main__":
    main() 