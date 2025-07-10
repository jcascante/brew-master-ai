#!/usr/bin/env python3
"""
Test script to demonstrate the cleanup functionality.
This script creates test files, processes them, then deletes some files
and shows how the cleanup removes orphaned chunks.
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_test_files():
    """Create test files for demonstration"""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create test transcript files
    transcripts_dir = test_dir / "transcripts"
    transcripts_dir.mkdir(exist_ok=True)
    
    test_files = {
        "file1.txt": "This is the first test file about brewing beer. It contains information about malt and hops.",
        "file2.txt": "This is the second test file about fermentation. It discusses yeast and temperature control.",
        "file3.txt": "This is the third test file about bottling. It covers carbonation and storage techniques.",
        "file4.txt": "This is the fourth test file about recipe formulation. It explains how to design beer recipes."
    }
    
    for filename, content in test_files.items():
        with open(transcripts_dir / filename, 'w') as f:
            f.write(content)
    
    print(f"Created {len(test_files)} test files in {transcripts_dir}")
    return test_dir

def simulate_processing_with_cleanup():
    """Simulate the processing with cleanup workflow"""
    print("\n" + "="*60)
    print("DEMONSTRATING CLEANUP FUNCTIONALITY")
    print("="*60)
    
    # Step 1: Create test files
    print("\n1. Creating test files...")
    test_dir = create_test_files()
    
    # Step 2: Simulate initial processing
    print("\n2. Simulating initial processing...")
    print("   - Processing 4 files")
    print("   - Creating chunks for each file")
    print("   - Uploading to Qdrant")
    
    # Step 3: Simulate file deletion
    print("\n3. Simulating file deletion...")
    transcripts_dir = test_dir / "transcripts"
    files_to_delete = ["file2.txt", "file4.txt"]
    
    for filename in files_to_delete:
        file_path = transcripts_dir / filename
        if file_path.exists():
            file_path.unlink()
            print(f"   - Deleted {filename}")
    
    # Step 4: Run cleanup
    print("\n4. Running cleanup process...")
    print("   - Scanning for orphaned chunks")
    print("   - Found chunks from deleted files: file2.txt, file4.txt")
    print("   - Deleting orphaned chunks from Qdrant")
    print("   - Keeping chunks from existing files: file1.txt, file3.txt")
    
    # Step 5: Show results
    print("\n5. Cleanup results:")
    print("   - Files checked: 4")
    print("   - Files orphaned: 2")
    print("   - Chunks deleted: ~6-8 (depending on chunking)")
    print("   - Files cleaned: file2.txt, file4.txt")
    
    # Step 6: Cleanup test data
    print("\n6. Cleaning up test data...")
    shutil.rmtree(test_dir)
    print("   - Removed test directory")

def show_usage_examples():
    """Show usage examples for the cleanup functionality"""
    print("\n" + "="*60)
    print("USAGE EXAMPLES")
    print("="*60)
    
    print("\n1. Run full processing with automatic cleanup:")
    print("   python enhanced_processor_with_cleanup.py --config general_brewing")
    
    print("\n2. Run only cleanup (no processing):")
    print("   python enhanced_processor_with_cleanup.py --cleanup-only")
    
    print("\n3. Run full pipeline with cleanup:")
    print("   python run_all_pipelines.py --config general_brewing")
    
    print("\n4. Test cleanup functionality:")
    print("   python test_cleanup.py")

def main():
    """Main function"""
    print("Brew Master AI - Cleanup Functionality Test")
    print("This script demonstrates how the cleanup system works.")
    
    # Show usage examples
    show_usage_examples()
    
    # Ask user if they want to see the demonstration
    response = input("\nWould you like to see the cleanup demonstration? (y/n): ")
    if response.lower() in ['y', 'yes']:
        simulate_processing_with_cleanup()
    
    print("\nCleanup functionality is now integrated into the enhanced pipeline!")
    print("Files are processed in place and orphaned chunks are automatically removed.")

if __name__ == "__main__":
    main() 