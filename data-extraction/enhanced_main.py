#!/usr/bin/env python3
"""
Enhanced Brew Master AI Data Extraction CLI
Features advanced chunking strategies, data validation, and quality assessment.
"""

import argparse
import os
import sys
from pathlib import Path

# Import our enhanced modules
from enhanced_processor import create_enhanced_embeddings, ProcessingConfig
from chunking_configs import get_config, list_available_configs, create_custom_config
from data_validator import DataQualityAnalyzer

def extract_audio(input_dir, output_dir, processed_dir):
    """Extract audio from video files using ffmpeg"""
    import subprocess
    import shutil
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.mp4'):
            input_path = os.path.join(input_dir, filename)
            base = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, base + '.wav')
            print(f'Extracting audio from {filename}...')
            
            try:
                subprocess.run([
                    'ffmpeg', '-y', '-i', input_path, '-vn', '-acodec', 'pcm_s16le', 
                    '-ar', '16000', '-ac', '1', output_path
                ], check=True, capture_output=True)
                print(f'Audio saved to {output_path}')
                
                # Move processed video
                processed_path = os.path.join(processed_dir, filename)
                shutil.move(input_path, processed_path)
                print(f'Moved {filename} to {processed_dir}')
                
            except subprocess.CalledProcessError as e:
                print(f'Error extracting audio from {filename}: {e}')
            except Exception as e:
                print(f'Unexpected error processing {filename}: {e}')

def transcribe_audio(audio_dir, transcript_dir, processed_audio_dir):
    """Transcribe audio files using Whisper"""
    import whisper
    import shutil
    
    os.makedirs(transcript_dir, exist_ok=True)
    os.makedirs(processed_audio_dir, exist_ok=True)
    
    print("Loading Whisper model...")
    model = whisper.load_model('base')
    
    for filename in os.listdir(audio_dir):
        if filename.lower().endswith('.wav'):
            audio_path = os.path.join(audio_dir, filename)
            base = os.path.splitext(filename)[0]
            transcript_path = os.path.join(transcript_dir, base + '.txt')
            
            print(f'Transcribing {filename}...')
            try:
                result = model.transcribe(audio_path)
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
                print(f'Transcript saved to {transcript_path}')
                
                # Move processed audio
                processed_path = os.path.join(processed_audio_dir, filename)
                shutil.move(audio_path, processed_path)
                print(f'Moved {filename} to {processed_audio_dir}')
                
            except Exception as e:
                print(f'Error transcribing {filename}: {e}')

def extract_pptx_images(pptx_dir, images_dir, processed_pptx_dir):
    """Extract images from PowerPoint presentations"""
    from pptx import Presentation
    import shutil
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(processed_pptx_dir, exist_ok=True)
    
    for filename in os.listdir(pptx_dir):
        if filename.lower().endswith('.pptx'):
            pptx_path = os.path.join(pptx_dir, filename)
            base = os.path.splitext(filename)[0]
            
            print(f'Extracting images from {filename}...')
            try:
                pres = Presentation(pptx_path)
                img_count = 0
                
                for i, slide in enumerate(pres.slides):
                    for shape in slide.shapes:
                        if hasattr(shape, 'image'):
                            img = shape.image
                            ext = img.ext
                            img_bytes = img.blob
                            img_filename = f"{base}_slide{i+1}_img{img_count+1}.{ext}"
                            img_path = os.path.join(images_dir, img_filename)
                            
                            with open(img_path, 'wb') as f:
                                f.write(img_bytes)
                            print(f"Extracted image: {img_path}")
                            img_count += 1
                
                # Move processed pptx
                processed_path = os.path.join(processed_pptx_dir, filename)
                shutil.move(pptx_path, processed_path)
                print(f"Moved {filename} to {processed_pptx_dir}")
                
            except Exception as e:
                print(f'Error processing {filename}: {e}')

def ocr_images(images_dir, texts_dir, processed_images_dir):
    """Extract text from images using OCR"""
    import pytesseract
    from PIL import Image
    import shutil
    
    os.makedirs(texts_dir, exist_ok=True)
    os.makedirs(processed_images_dir, exist_ok=True)
    
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(images_dir, filename)
            base = os.path.splitext(filename)[0]
            text_path = os.path.join(texts_dir, base + '.txt')
            
            print(f'Running OCR on {filename}...')
            try:
                text = pytesseract.image_to_string(Image.open(image_path))
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f'OCR text saved to {text_path}')
                
                # Move processed image
                processed_path = os.path.join(processed_images_dir, filename)
                shutil.move(image_path, processed_path)
                print(f'Moved {filename} to {processed_images_dir}')
                
            except Exception as e:
                print(f'Error processing {filename}: {e}')

def validate_data(directory_path, output_report=None, create_plots=False):
    """Validate and analyze data quality"""
    print(f"Validating data in: {directory_path}")
    
    analyzer = DataQualityAnalyzer()
    results = analyzer.analyze_directory(directory_path)
    
    # Generate report
    report = analyzer.generate_report(results, output_report)
    print(report)
    
    # Create visualizations if requested
    if create_plots:
        try:
            analyzer.create_visualizations(results, "quality_plots")
            print("Visualizations created in 'quality_plots' directory")
        except Exception as e:
            print(f"Could not create visualizations: {e}")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Brew Master AI Data Extraction CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract audio from videos
  python enhanced_main.py --extract-audio
  
  # Transcribe audio with quality validation
  python enhanced_main.py --transcribe-audio --validate
  
  # Create embeddings with custom chunking
  python enhanced_main.py --create-embeddings --config technical_brewing
  
  # Validate existing data
  python enhanced_main.py --validate data/transcripts --report quality_report.txt
  
  # List available configurations
  python enhanced_main.py --list-configs
        """
    )
    
    # Data extraction commands
    parser.add_argument('--extract-audio', action='store_true', 
                       help='Extract audio from videos')
    parser.add_argument('--transcribe-audio', action='store_true', 
                       help='Transcribe audio to text')
    parser.add_argument('--extract-pptx-images', action='store_true', 
                       help='Extract images from PowerPoint presentations')
    parser.add_argument('--ocr-images', action='store_true', 
                       help='Extract text from images using OCR')
    
    # Enhanced embedding creation
    parser.add_argument('--create-embeddings', action='store_true', 
                       help='Create enhanced embeddings and upload to Qdrant')
    parser.add_argument('--config', type=str, default='general_brewing',
                       help='Chunking configuration preset (use --list-configs to see options)')
    
    # Data validation
    parser.add_argument('--validate', type=str, metavar='DIRECTORY',
                       help='Validate data quality in specified directory')
    parser.add_argument('--report', type=str, metavar='FILE',
                       help='Output file for quality report')
    parser.add_argument('--plots', action='store_true',
                       help='Create quality visualization plots')
    
    # Configuration management
    parser.add_argument('--list-configs', action='store_true',
                       help='List available chunking configurations')
    
    # Custom chunking parameters
    parser.add_argument('--chunk-size', type=int, metavar='SIZE',
                       help='Custom maximum chunk size in characters')
    parser.add_argument('--overlap', type=int, metavar='SIZE',
                       help='Custom overlap size between chunks')
    parser.add_argument('--min-chunk', type=int, metavar='SIZE',
                       help='Custom minimum chunk size')
    parser.add_argument('--max-sentences', type=int, metavar='COUNT',
                       help='Custom maximum sentences per chunk')
    
    args = parser.parse_args()
    
    # List configurations
    if args.list_configs:
        list_available_configs()
        return
    
    # Validate data
    if args.validate:
        validate_data(args.validate, args.report, args.plots)
        return
    
    # Data extraction pipeline
    if args.extract_audio:
        extract_audio('data/videos', 'data/audios', 'data/processed')
    
    if args.transcribe_audio:
        transcribe_audio('data/audios', 'data/transcripts', 'data/processed_audios')
        if args.validate:
            print("\nValidating transcripts...")
            validate_data('data/transcripts', args.report, args.plots)
    
    if args.extract_pptx_images:
        extract_pptx_images('data/presentations', 'data/presentation_images', 'data/processed_presentations')
    
    if args.ocr_images:
        ocr_images('data/presentation_images', 'data/presentation_texts', 'data/processed_images')
        if args.validate:
            print("\nValidating OCR text...")
            validate_data('data/presentation_texts', args.report, args.plots)
    
    # Create enhanced embeddings
    if args.create_embeddings:
        print(f"Creating embeddings with configuration: {args.config}")
        
        # Get configuration
        if args.chunk_size or args.overlap or args.min_chunk or args.max_sentences:
            # Use custom configuration
            config = create_custom_config(
                max_chunk_size=args.chunk_size or 1000,
                overlap_size=args.overlap or 200,
                min_chunk_size=args.min_chunk or 150,
                max_sentences_per_chunk=args.max_sentences or 10
            )
            print("Using custom chunking configuration")
        else:
            # Use preset configuration
            config = get_config(args.config)
            print(f"Using preset configuration: {args.config}")
        
        create_enhanced_embeddings(config)
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()

if __name__ == '__main__':
    main() 