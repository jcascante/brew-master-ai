#!/usr/bin/env python3
"""
Test script to demonstrate smart config selection functionality.
This script shows how the system automatically selects appropriate configs
for different content types and prevents duplicate processing.
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_test_files():
    """Create test files for demonstration"""
    test_dir = Path("test_smart_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create test transcript files
    transcripts_dir = test_dir / "transcripts"
    transcripts_dir.mkdir(exist_ok=True)
    
    # Create test OCR files
    ocr_dir = test_dir / "presentation_texts"
    ocr_dir.mkdir(exist_ok=True)
    
    transcript_files = {
        "video_transcript1.txt": "This is a long video transcript about brewing beer. It contains detailed information about the brewing process, including mashing, boiling, and fermentation techniques. The transcript covers various aspects of home brewing and commercial brewing methods.",
        "video_transcript2.txt": "Another video transcript discussing beer styles and recipes. This content includes information about different types of malt, hops, and yeast used in brewing various beer styles like IPAs, stouts, and lagers."
    }
    
    ocr_files = {
        "presentation_slide1.txt": "Brewing Process Overview. Step 1: Mashing. Step 2: Boiling. Step 3: Fermentation. Key ingredients: malt, hops, yeast, water.",
        "presentation_slide2.txt": "Beer Styles. Ale: Top-fermented. Lager: Bottom-fermented. Common styles: IPA, Stout, Pilsner, Wheat Beer."
    }
    
    for filename, content in transcript_files.items():
        with open(transcripts_dir / filename, 'w') as f:
            f.write(content)
    
    for filename, content in ocr_files.items():
        with open(ocr_dir / filename, 'w') as f:
            f.write(content)
    
    print(f"Created {len(transcript_files)} transcript files and {len(ocr_files)} OCR files")
    return test_dir

def simulate_smart_config_selection():
    """Simulate the smart config selection workflow"""
    print("\n" + "="*60)
    print("DEMONSTRATING SMART CONFIG SELECTION")
    print("="*60)
    
    # Step 1: Create test files
    print("\n1. Creating test files...")
    test_dir = create_test_files()
    
    # Step 2: Show smart config mapping
    print("\n2. Smart Config Selection Rules:")
    print("   - Transcript files → 'video_transcript' config (longer chunks, more overlap)")
    print("   - OCR files → 'presentation_text' config (shorter chunks, focused)")
    print("   - Manual override available with --config parameter")
    
    # Step 3: Simulate first run
    print("\n3. First Run (Auto-config selection):")
    print("   - Processing transcripts with 'video_transcript' config")
    print("   - Processing OCR with 'presentation_text' config")
    print("   - Files processed: 4")
    print("   - Files skipped: 0")
    
    # Step 4: Simulate second run (same files)
    print("\n4. Second Run (Same files):")
    print("   - Same smart config selection applied")
    print("   - Files processed: 0 (all skipped due to deduplication)")
    print("   - Files skipped: 4 (already processed with same config)")
    
    # Step 5: Simulate third run (manual override)
    print("\n5. Third Run (Manual override --config general_brewing):")
    print("   - Manual config 'general_brewing' overrides smart selection")
    print("   - Files processed: 4 (reprocessed with different config)")
    print("   - Files skipped: 0")
    print("   - Note: This creates different chunks but tracks config used")
    
    # Step 6: Show benefits
    print("\n6. Benefits of Smart Config Selection:")
    print("   ✅ Automatic optimal config for each content type")
    print("   ✅ Prevents duplicate processing with same config")
    print("   ✅ Allows manual override when needed")
    print("   ✅ Tracks which config was used for each file")
    print("   ✅ Efficient processing and storage")
    
    # Step 7: Cleanup
    print("\n7. Cleaning up test data...")
    shutil.rmtree(test_dir)
    print("   - Removed test directory")

def show_usage_examples():
    """Show usage examples for smart config selection"""
    print("\n" + "="*60)
    print("USAGE EXAMPLES")
    print("="*60)
    
    print("\n1. Auto-config selection (recommended):")
    print("   python enhanced_processor_with_cleanup.py")
    print("   # Automatically uses 'video_transcript' for transcripts")
    print("   # Automatically uses 'presentation_text' for OCR")
    
    print("\n2. Manual config override:")
    print("   python enhanced_processor_with_cleanup.py --config technical_brewing")
    print("   # Forces all content to use 'technical_brewing' config")
    
    print("\n3. Full pipeline with smart config:")
    print("   python run_all_pipelines.py")
    print("   # Complete pipeline with automatic config selection")
    
    print("\n4. Cleanup only:")
    print("   python enhanced_processor_with_cleanup.py --cleanup-only")
    print("   # Only removes orphaned chunks, no processing")

def main():
    """Main function"""
    print("Brew Master AI - Smart Config Selection Test")
    print("This script demonstrates how the system automatically selects")
    print("appropriate chunking configurations for different content types.")
    
    # Show usage examples
    show_usage_examples()
    
    # Ask user if they want to see the demonstration
    response = input("\nWould you like to see the smart config selection demonstration? (y/n): ")
    if response.lower() in ['y', 'yes']:
        simulate_smart_config_selection()
    
    print("\nSmart config selection is now integrated into the enhanced pipeline!")
    print("The system automatically chooses the best config for each content type.")
    print("No more duplicate processing or manual config selection needed!")

if __name__ == "__main__":
    main() 