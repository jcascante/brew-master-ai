#!/usr/bin/env python3
"""
Run the full Brew Master AI data pipeline:
- Extract audio from videos
- Transcribe audio
- Extract images from presentations
- OCR images
- Validate transcripts and OCR text
- Create embeddings and upload to Qdrant
- Print a sample of the resulting metadata

Usage:
    python run_all_pipelines.py --config <preset>

Example:
    python run_all_pipelines.py --config video_transcript
    python run_all_pipelines.py --config balanced

See ENHANCED_README.md for more details on available configs.
"""

import os
import sys
import random
import argparse
from pathlib import Path

from enhanced_main import extract_audio, transcribe_audio, extract_pptx_images, ocr_images
from chunking_configs import get_config, list_available_configs
from data_validator import DataQualityAnalyzer
from enhanced_processor import create_enhanced_embeddings, EnhancedDataProcessor

DATA_DIR = Path("data")

# Helper to print a separator
sep = lambda: print("\n" + "="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Run all Brew Master AI data pipelines")
    parser.add_argument('--config', type=str, default='general_brewing',
                        help='Chunking config preset (see --list-configs)')
    parser.add_argument('--list-configs', action='store_true', help='List available chunking configs')
    args = parser.parse_args()

    if args.list_configs:
        list_available_configs()
        sys.exit(0)

    config = get_config(args.config)
    sep()
    print(f"[1/7] Extracting audio from videos...")
    extract_audio(DATA_DIR / 'videos', DATA_DIR / 'audios', DATA_DIR / 'processed')

    sep()
    print(f"[2/7] Transcribing audio to text...")
    transcribe_audio(DATA_DIR / 'audios', DATA_DIR / 'transcripts', DATA_DIR / 'processed_audios')

    sep()
    print(f"[3/7] Extracting images from presentations...")
    extract_pptx_images(DATA_DIR / 'presentations', DATA_DIR / 'presentation_images', DATA_DIR / 'processed_presentations')

    sep()
    print(f"[4/7] Running OCR on images...")
    ocr_images(DATA_DIR / 'presentation_images', DATA_DIR / 'presentation_texts', DATA_DIR / 'processed_images')

    sep()
    print(f"[5/7] Validating transcripts...")
    transcript_validator = DataQualityAnalyzer()
    transcript_results = transcript_validator.analyze_directory(str(DATA_DIR / 'transcripts'))
    print(transcript_validator.generate_report(transcript_results))

    sep()
    print(f"[6/7] Validating OCR text...")
    ocr_validator = DataQualityAnalyzer()
    ocr_results = ocr_validator.analyze_directory(str(DATA_DIR / 'presentation_texts'))
    print(ocr_validator.generate_report(ocr_results))

    sep()
    print(f"[7/7] Creating embeddings and uploading to Qdrant (config: {args.config})...")
    create_enhanced_embeddings(config)

    sep()
    print("✅ All pipelines completed!\n")
    print(f"Sample metadata from uploaded chunks (showing 1 random chunk):")
    # Show a sample chunk's metadata
    processor = EnhancedDataProcessor(config)
    all_chunks = []
    if os.path.exists(DATA_DIR / 'transcripts'):
        all_chunks.extend(processor.process_directory(str(DATA_DIR / 'transcripts'), 'transcript'))
    if os.path.exists(DATA_DIR / 'presentation_texts'):
        all_chunks.extend(processor.process_directory(str(DATA_DIR / 'presentation_texts'), 'ocr'))
    if all_chunks:
        sample_chunk = random.choice(all_chunks)
        print("--- Sample Chunk Metadata ---")
        print("Text (first 200 chars):", sample_chunk[0][:200] + ("..." if len(sample_chunk[0]) > 200 else ""))
        print("Metadata:")
        for k, v in sample_chunk[1].items():
            print(f"  {k}: {v}")
    else:
        print("No chunks found to display metadata sample.")
    sep()
    print("Next steps:")
    print("- You can now query your Qdrant vector DB with the backend RAG system.")
    print("- Review quality reports above for any data issues.")
    print("- For more options, see ENHANCED_README.md.")

if __name__ == "__main__":
    main() 