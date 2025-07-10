#!/usr/bin/env python3
"""
Test script for the enhanced data processing pipeline.
Demonstrates chunking strategies, validation, and quality assessment.
"""

import os
import tempfile
from pathlib import Path

# Import our enhanced modules
from enhanced_processor import ProcessingConfig, ChunkConfig
from chunking_configs import get_config, list_available_configs
from data_validator import DataQualityAnalyzer

def create_sample_data():
    """Create sample brewing content for testing"""
    sample_texts = {
        "brewing_basics.txt": """
        Beer brewing is a fascinating process that combines art and science. The basic steps include malting, mashing, boiling, fermentation, and conditioning. 
        
        Malting involves soaking barley in water and allowing it to germinate, then drying it to create malt. The malt is then crushed and mixed with hot water in a process called mashing. During mashing, enzymes convert the starches in the malt into fermentable sugars.
        
        The resulting liquid, called wort, is then boiled with hops. Hops add bitterness, flavor, and aroma to the beer. They also act as a natural preservative. After boiling, the wort is cooled and yeast is added to begin fermentation.
        
        Fermentation is where the magic happens. Yeast consumes the sugars and produces alcohol and carbon dioxide. This process typically takes one to two weeks. After fermentation, the beer is conditioned, which allows flavors to mature and develop.
        
        The final step is packaging the beer in bottles or kegs. Proper packaging ensures the beer maintains its quality and carbonation. Homebrewers can create a wide variety of beer styles, from light lagers to dark stouts, by adjusting ingredients and brewing techniques.
        """,
        
        "recipe_ipa.txt": """
        India Pale Ale (IPA) Recipe
        
        Ingredients:
        - 12 lbs Pale Ale Malt
        - 1 lb Crystal 40L Malt
        - 2 oz Cascade Hops (60 min)
        - 1 oz Centennial Hops (15 min)
        - 1 oz Citra Hops (5 min)
        - 1 oz Mosaic Hops (dry hop)
        - Wyeast 1056 American Ale Yeast
        
        Mash Schedule:
        - Mash in at 152°F (67°C) for 60 minutes
        - Sparge with 170°F (77°C) water
        
        Boil Schedule:
        - 60-minute boil
        - Add Cascade hops at start of boil
        - Add Centennial hops with 15 minutes remaining
        - Add Citra hops with 5 minutes remaining
        
        Fermentation:
        - Pitch yeast at 68°F (20°C)
        - Ferment for 7 days
        - Add Mosaic hops for dry hopping
        - Condition for 7 more days
        
        Expected Results:
        - Original Gravity: 1.065
        - Final Gravity: 1.015
        - ABV: 6.5%
        - IBU: 65
        - SRM: 8
        """,
        
        "equipment_guide.txt": """
        Essential Homebrewing Equipment
        
        Brewing Kettle: A large pot, typically 8-10 gallons, for boiling wort. Stainless steel is preferred for durability and heat distribution.
        
        Mash Tun: A vessel for mashing grains. Can be a converted cooler or dedicated mash tun with false bottom for lautering.
        
        Fermenter: A container for fermentation. Glass carboys or plastic buckets work well. Ensure it's food-grade and has an airlock.
        
        Thermometer: Essential for monitoring mash and fermentation temperatures. Digital thermometers are more accurate.
        
        Hydrometer: Measures specific gravity to track fermentation progress and calculate alcohol content.
        
        Bottles or Kegs: For packaging finished beer. Bottles should be cleaned and sanitized. Kegs require a CO2 system.
        
        Sanitizer: Critical for preventing contamination. Star San or similar no-rinse sanitizers are recommended.
        
        Additional Tools: Wort chiller, stirring spoon, measuring cups, and a scale for weighing ingredients.
        """
    }
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="brew_test_")
    print(f"Created test directory: {test_dir}")
    
    # Write sample files
    for filename, content in sample_texts.items():
        file_path = os.path.join(test_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created: {filename}")
    
    return test_dir

def test_chunking_configs():
    """Test different chunking configurations"""
    print("\n" + "="*60)
    print("TESTING CHUNKING CONFIGURATIONS")
    print("="*60)
    
    # List available configurations
    print("\nAvailable configurations:")
    list_available_configs()
    
    # Test different presets
    presets_to_test = ['video_transcript', 'presentation_text', 'recipe_content', 'technical_brewing']
    
    for preset_name in presets_to_test:
        print(f"\n--- Testing {preset_name} preset ---")
        config = get_config(preset_name)
        
        print(f"Max chunk size: {config.chunk_config.max_chunk_size}")
        print(f"Overlap size: {config.chunk_config.overlap_size}")
        print(f"Max sentences per chunk: {config.chunk_config.max_sentences_per_chunk}")
        print(f"Chunk by sentences: {config.chunk_config.chunk_by_sentences}")

def test_data_validation(test_dir):
    """Test data validation and quality assessment"""
    print("\n" + "="*60)
    print("TESTING DATA VALIDATION")
    print("="*60)
    
    analyzer = DataQualityAnalyzer()
    
    print(f"\nAnalyzing test directory: {test_dir}")
    results = analyzer.analyze_directory(test_dir)
    
    # Generate and display report
    report = analyzer.generate_report(results)
    print("\nQuality Report:")
    print(report)
    
    # Try to create visualizations
    try:
        plots_dir = os.path.join(test_dir, "quality_plots")
        analyzer.create_visualizations(results, plots_dir)
        print(f"\nVisualizations created in: {plots_dir}")
    except Exception as e:
        print(f"\nCould not create visualizations: {e}")

def test_enhanced_processing(test_dir):
    """Test the enhanced processing pipeline"""
    print("\n" + "="*60)
    print("TESTING ENHANCED PROCESSING")
    print("="*60)
    
    from enhanced_processor import EnhancedDataProcessor
    
    # Test with different configurations
    configs_to_test = [
        ('general_brewing', get_config('general_brewing')),
        ('technical_brewing', get_config('technical_brewing')),
        ('recipe_content', get_config('recipe_content'))
    ]
    
    for config_name, config in configs_to_test:
        print(f"\n--- Testing {config_name} configuration ---")
        
        processor = EnhancedDataProcessor(config)
        
        # Process the test directory
        chunks = processor.process_directory(test_dir, 'test_content')
        
        print(f"Created {len(chunks)} chunks")
        
        # Show statistics
        stats = processor.get_statistics()
        print(f"Files processed: {stats['files_processed']}")
        print(f"Chunks created: {stats['chunks_created']}")
        print(f"Chunks validated: {stats['chunks_validated']}")
        print(f"Chunks rejected: {stats['chunks_rejected']}")
        
        # Show sample chunks
        if chunks:
            print(f"\nSample chunk (first 200 chars):")
            sample_text = chunks[0][0][:200] + "..." if len(chunks[0][0]) > 200 else chunks[0][0]
            print(f"Text: {sample_text}")
            print(f"Metadata keys: {list(chunks[0][1].keys())}")

def main():
    """Main test function"""
    print("🍺 Enhanced Data Processing Pipeline Test")
    print("="*60)
    
    # Create sample data
    test_dir = create_sample_data()
    
    try:
        # Test chunking configurations
        test_chunking_configs()
        
        # Test data validation
        test_data_validation(test_dir)
        
        # Test enhanced processing
        test_enhanced_processing(test_dir)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nTest data created in: {test_dir}")
        print("You can inspect the files and quality reports to see the results.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print(f"\nCleaning up test directory: {test_dir}")
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    main() 