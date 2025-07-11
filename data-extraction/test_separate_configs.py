#!/usr/bin/env python3
"""
Test script to demonstrate separate preprocessing and chunking configurations.
This script shows how you can mix and match different preprocessing and chunking
strategies for optimal results.
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_test_files():
    """Create test files for demonstration"""
    test_dir = Path("test_separate_configs")
    test_dir.mkdir(exist_ok=True)
    
    # Create test transcript files
    transcripts_dir = test_dir / "transcripts"
    transcripts_dir.mkdir(exist_ok=True)
    
    # Create test OCR files
    ocr_dir = test_dir / "presentation_texts"
    ocr_dir.mkdir(exist_ok=True)
    
    transcript_files = {
        "technical_transcript.txt": "This is a TECHNICAL transcript about brewing beer with specific measurements like 15.5°P gravity, 45 IBU, and pH 5.2. It contains detailed information about the brewing process, including mashing at 152°F, boiling for 60 minutes, and fermentation at 68°F. The transcript covers various aspects of home brewing and commercial brewing methods with precise technical specifications.",
        "casual_transcript.txt": "So, like, this is a casual transcript about brewing beer, you know? It's got some, um, informal language and stuff. We're talking about making beer at home, which is pretty cool. There's some filler words and casual expressions throughout the content."
    }
    
    ocr_files = {
        "technical_slide.txt": "BREWING PROCESS: Step 1: Mashing (152°F, 60 min). Step 2: Boiling (212°F, 60 min). Step 3: Fermentation (68°F, 14 days). Key ingredients: MALT, HOPS, YEAST, WATER. Technical specifications: OG: 1.050, FG: 1.012, ABV: 5.0%.",
        "casual_slide.txt": "Beer Styles Overview. Ale: Top-fermented yeast. Lager: Bottom-fermented yeast. Common styles: IPA, Stout, Pilsner, Wheat Beer. Basic info for beginners."
    }
    
    for filename, content in transcript_files.items():
        with open(transcripts_dir / filename, 'w') as f:
            f.write(content)
    
    for filename, content in ocr_files.items():
        with open(ocr_dir / filename, 'w') as f:
            f.write(content)
    
    print(f"Created {len(transcript_files)} transcript files and {len(ocr_files)} OCR files")
    return test_dir

def demonstrate_separate_configs():
    """Demonstrate the separate configuration system"""
    print("\n" + "="*60)
    print("DEMONSTRATING SEPARATE PREPROCESSING & CHUNKING CONFIGS")
    print("="*60)
    
    # Step 1: Create test files
    print("\n1. Creating test files...")
    test_dir = create_test_files()
    
    # Step 2: Show available configs
    print("\n2. Available Configuration Types:")
    print("   📝 Preprocessing Configs:")
    print("     - light_preprocessing: Minimal changes, preserve original")
    print("     - standard_preprocessing: Balanced cleaning")
    print("     - aggressive_preprocessing: Heavy cleaning, remove stopwords")
    print("     - technical_preprocessing: Preserve case, numbers, technical terms")
    
    print("\n   🧩 Chunking Configs:")
    print("     - video_transcript: Long chunks (1500 chars, 300 overlap)")
    print("     - presentation_text: Short chunks (800 chars, 150 overlap)")
    print("     - technical_brewing: Medium chunks (1200 chars, 250 overlap)")
    print("     - fast_chunking: Character-based, fast processing")
    
    # Step 3: Show example combinations
    print("\n3. Example Config Combinations:")
    
    combinations = [
        ("Technical Content", "technical_preprocessing", "technical_brewing"),
        ("Fast Processing", "aggressive_preprocessing", "fast_chunking"),
        ("Preserve Original", "light_preprocessing", "video_transcript"),
        ("Balanced Approach", "standard_preprocessing", "general_brewing")
    ]
    
    for name, prep, chunk in combinations:
        print(f"   {name}: {prep} + {chunk}")
    
    # Step 4: Show usage examples
    print("\n4. Usage Examples:")
    print("   # Use combined preset (recommended for most cases)")
    print("   python enhanced_processor_with_cleanup.py --config technical_brewing")
    
    print("\n   # Create custom combination")
    print("   from chunking_configs import create_custom_combination")
    print("   config = create_custom_combination('technical_preprocessing', 'video_transcript')")
    
    print("\n   # Create fully custom config")
    print("   from chunking_configs import create_custom_config")
    print("   config = create_custom_config(")
    print("       # Preprocessing")
    print("       clean_text=True, remove_stopwords=False, lemmatize=False,")
    print("       min_text_length=100, max_text_length=12000,")
    print("       lowercase=False, remove_numbers=False,")
    print("       # Chunking")
    print("       max_chunk_size=1500, overlap_size=300,")
    print("       chunk_by_sentences=True, max_sentences_per_chunk=15")
    print("   )")
    
    # Step 5: Show benefits
    print("\n5. Benefits of Separate Configs:")
    print("   ✅ Mix and match preprocessing and chunking strategies")
    print("   ✅ Optimize for specific content types")
    print("   ✅ Preserve technical terms while using optimal chunking")
    print("   ✅ Fast preprocessing with detailed chunking (or vice versa)")
    print("   ✅ Fine-grained control over the entire pipeline")
    
    # Step 6: Show practical scenarios
    print("\n6. Practical Scenarios:")
    print("   📊 Technical Documents:")
    print("     - Preprocessing: technical_preprocessing (preserve case, numbers)")
    print("     - Chunking: technical_brewing (medium chunks, preserve context)")
    
    print("\n   🎥 Video Transcripts:")
    print("     - Preprocessing: light_preprocessing (minimal changes)")
    print("     - Chunking: video_transcript (long chunks, maintain narrative)")
    
    print("\n   📋 Presentation Slides:")
    print("     - Preprocessing: standard_preprocessing (balanced cleaning)")
    print("     - Chunking: presentation_text (short chunks, focused info)")
    
    print("\n   ⚡ Fast Processing:")
    print("     - Preprocessing: aggressive_preprocessing (remove stopwords, lemmatize)")
    print("     - Chunking: fast_chunking (character-based, no sentence boundaries)")
    
    # Step 7: Cleanup
    print("\n7. Cleaning up test data...")
    shutil.rmtree(test_dir)
    print("   - Removed test directory")

def show_advanced_usage():
    """Show advanced usage examples"""
    print("\n" + "="*60)
    print("ADVANCED USAGE EXAMPLES")
    print("="*60)
    
    print("\n1. List All Available Configs:")
    print("   python enhanced_main.py --list-configs")
    
    print("\n2. Create Custom Combination in Code:")
    print("   from chunking_configs import create_custom_combination")
    print("   config = create_custom_combination('technical_preprocessing', 'video_transcript')")
    print("   create_enhanced_embeddings_with_cleanup(config)")
    
    print("\n3. Create Fully Custom Config:")
    print("   from chunking_configs import create_custom_config")
    print("   config = create_custom_config(")
    print("       # Preprocessing settings")
    print("       clean_text=True, remove_stopwords=False, lemmatize=False,")
    print("       min_text_length=100, max_text_length=15000,")
    print("       normalize_unicode=True, remove_special_chars=False,")
    print("       lowercase=False, remove_numbers=False, remove_punctuation=False,")
    print("       # Chunking settings")
    print("       max_chunk_size=1500, min_chunk_size=200, overlap_size=300,")
    print("       chunk_by_sentences=True, preserve_paragraphs=True,")
    print("       max_sentences_per_chunk=15, respect_sentence_boundaries=True,")
    print("       smart_boundaries=True")
    print("   )")
    
    print("\n4. Access Individual Configs:")
    print("   from chunking_configs import get_preprocessing_config, get_chunking_config")
    print("   prep_config = get_preprocessing_config('technical_preprocessing')")
    print("   chunk_config = get_chunking_config('video_transcript')")
    print("   config = ProcessingConfig(preprocessing=prep_config, chunking=chunk_config)")

def main():
    """Main function"""
    print("Brew Master AI - Separate Configuration System Test")
    print("This script demonstrates the new separate preprocessing and chunking")
    print("configuration system for maximum flexibility.")
    
    # Show advanced usage
    show_advanced_usage()
    
    # Ask user if they want to see the demonstration
    response = input("\nWould you like to see the separate configs demonstration? (y/n): ")
    if response.lower() in ['y', 'yes']:
        demonstrate_separate_configs()
    
    print("\nSeparate preprocessing and chunking configs are now available!")
    print("You can mix and match different strategies for optimal results.")
    print("Use --list-configs to see all available options.")

if __name__ == "__main__":
    main() 