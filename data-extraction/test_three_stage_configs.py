#!/usr/bin/env python3
"""
Test script to demonstrate the three-stage configuration system:
1. InputProcessingConfig (raw input → text)
2. PreprocessingConfig (text cleaning/normalization)
3. TextProcessingConfig (chunking, embedding, vector store)
"""

from chunking_configs import (
    INPUT_PROCESSING_PRESETS,
    PREPROCESSING_PRESETS,
    TEXT_PROCESSING_PRESETS,
    create_custom_combination,
    list_available_configs
)


def print_config_details(config):
    print("\n=== INPUT PROCESSING CONFIG ===")
    for k, v in vars(config.input_processing).items():
        print(f"{k}: {v}")
    print("\n=== PREPROCESSING CONFIG ===")
    for k, v in vars(config.preprocessing).items():
        print(f"{k}: {v}")
    print("\n=== TEXT PROCESSING CONFIG ===")
    for k, v in vars(config.text_processing).items():
        print(f"{k}: {v}")


def demonstrate_three_stage_configs():
    print("\n" + "="*60)
    print("DEMONSTRATING THREE-STAGE CONFIGURATION SYSTEM")
    print("="*60)

    # Step 1: List available configs
    print("\n1. Listing available configuration presets:")
    list_available_configs()

    # Step 2: Show example combinations
    print("\n2. Example Config Combinations:")
    combos = [
        ("High Quality Video Pipeline", "high_quality_input", "light_preprocessing", "video_transcript"),
        ("Technical Brewing Pipeline", "technical_input", "technical_preprocessing", "technical_brewing"),
        ("Fast OCR Pipeline", "fast_input", "aggressive_preprocessing", "fast_chunking"),
        ("Balanced General Pipeline", "balanced_input", "standard_preprocessing", "general_brewing"),
    ]
    for name, input_p, prep_p, text_p in combos:
        print(f"  {name}: {input_p} + {prep_p} + {text_p}")

    # Step 3: Create and print a config
    print("\n3. Creating and displaying a custom config:")
    config = create_custom_combination("technical_input", "technical_preprocessing", "technical_brewing")
    print_config_details(config)

    # Step 4: Usage example
    print("\n4. Usage Example:")
    print("   from chunking_configs import create_custom_combination")
    print("   config = create_custom_combination('technical_input', 'technical_preprocessing', 'technical_brewing')")
    print("   # Use config.input_processing, config.preprocessing, config.text_processing in your pipeline")

    print("\nThree-stage configuration system is ready for use!")

if __name__ == "__main__":
    demonstrate_three_stage_configs() 