# Whisper Optimization Guide for Spanish Audio

## Overview
This guide provides best practices for optimizing Whisper transcription for Spanish audio content, specifically focused on brewing and beer-making content.

## Model Selection

### Recommended Models (in order of preference):
1. **`medium`** - Best balance of accuracy and speed for Spanish
2. **`large`** - Highest accuracy, slower processing
3. **`small`** - Good accuracy, faster than medium
4. **`base`** - Decent accuracy, fast processing
5. **`tiny`** - Fastest, lowest accuracy (not recommended for Spanish)

### Why `medium` is recommended:
- Better Spanish language understanding
- Good balance between accuracy and processing time
- Handles brewing terminology well
- Reasonable memory usage

## Key Configuration Parameters

### 1. Language and Task
```python
language="es"  # Spanish language code
task="transcribe"  # For speech-to-text (not translation)
```

### 2. Temperature Control
```python
temperature=0.0  # Deterministic output, no randomness
```
- Use 0.0 for consistent, reproducible results
- Higher values (0.1-0.3) can help with unclear audio but may introduce errors

### 3. Audio Quality Filters
```python
compression_ratio_threshold=2.4  # Filter out non-speech segments
logprob_threshold=-1.0  # Filter low-confidence segments
no_speech_threshold=0.6  # Filter silence and background noise
```

### 4. Context and Continuity
```python
condition_on_previous_text=True  # Use context from previous segments
initial_prompt="Este es un audio sobre cerveza y técnicas de elaboración de cerveza artesanal."
```

### 5. Precision Settings
```python
fp16=False  # Use float32 for better accuracy (slower but more precise)
```

## Spanish-Specific Optimizations

### 1. Initial Prompt for Brewing Content
Use domain-specific prompts to improve accuracy:

```python
# General brewing context
initial_prompt="Este es un audio sobre cerveza y técnicas de elaboración de cerveza artesanal."

# More specific brewing terms
initial_prompt="Este audio trata sobre elaboración de cerveza, incluyendo términos como malta, lúpulo, levadura, fermentación, macerado, hervor, y técnicas de cerveza artesanal."

# Regional variations
initial_prompt="Este audio trata sobre cerveza artesanal con terminología en español de México/España/Argentina."
```

### 2. Common Spanish Brewing Terms
Include these terms in your initial prompt for better recognition:

**Ingredients:**
- malta, lúpulo, levadura, agua, trigo, cebada, centeno, avena

**Process:**
- macerado, hervor, fermentación, maduración, embotellado, carbonatación

**Beer Types:**
- lager, ale, stout, porter, ipa, pilsner, wheat beer, amber ale

**Equipment:**
- olla de hervor, fermentador, botella, barril, grifo, enfriador

## Audio Preprocessing

### 1. Sample Rate
```python
audio_sample_rate=16000  # Whisper's preferred sample rate
```

### 2. Audio Channels
```python
audio_channels=1  # Mono audio is sufficient for speech
```

### 3. Audio Quality
- Ensure audio is clear and has minimal background noise
- Normalize audio levels
- Remove echo and reverb if possible

## Advanced Techniques

### 1. Chunking Long Audio
For very long audio files (>30 minutes), consider chunking:

```python
def chunk_audio(audio_path, chunk_duration=1800):  # 30 minutes
    # Split audio into chunks and process separately
    # Then combine results
    pass
```

### 2. Post-Processing
After transcription, consider:

```python
def post_process_spanish_text(text):
    # Fix common Spanish transcription errors
    text = text.replace("q", "que")  # Common abbreviation
    text = text.replace("x", "por")  # Common abbreviation
    text = text.replace("d", "de")   # Common abbreviation
    
    # Fix brewing terminology
    text = text.replace("malta", "malta")
    text = text.replace("lupulo", "lúpulo")
    text = text.replace("levadura", "levadura")
    
    return text
```

### 3. Confidence Scoring
Use Whisper's confidence scores to filter results:

```python
def filter_by_confidence(segments, min_confidence=0.8):
    return [seg for seg in segments if seg['avg_logprob'] > min_confidence]
```

## Performance Optimization

### 1. Batch Processing
```python
# Process multiple files in parallel
from concurrent.futures import ThreadPoolExecutor

def process_audio_batch(audio_files, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(transcribe_audio, audio_files))
    return results
```

### 2. Memory Management
```python
# Clear model from memory after processing
import gc

def transcribe_with_cleanup(audio_path):
    model = whisper.load_model("medium")
    result = model.transcribe(audio_path)
    del model
    gc.collect()
    return result
```

## Troubleshooting

### Common Issues and Solutions:

1. **Poor Spanish Recognition**
   - Use `medium` or `large` model
   - Add Spanish-specific initial prompt
   - Ensure audio quality is good

2. **Brewing Terms Misunderstood**
   - Include brewing terminology in initial prompt
   - Use post-processing to fix common errors
   - Consider creating a custom vocabulary

3. **Background Noise**
   - Increase `no_speech_threshold` to 0.7-0.8
   - Use audio preprocessing to reduce noise
   - Consider using `compression_ratio_threshold`

4. **Slow Processing**
   - Use `small` model for faster processing
   - Enable `fp16=True` (slightly less accurate but faster)
   - Process in parallel

## Configuration Examples

### High Accuracy Configuration
```python
whisper_model = "large"
whisper_temperature = 0.0
whisper_fp16 = False
whisper_compression_ratio_threshold = 2.4
whisper_logprob_threshold = -1.0
whisper_no_speech_threshold = 0.6
whisper_condition_on_previous_text = True
whisper_initial_prompt = "Este es un audio sobre cerveza y técnicas de elaboración de cerveza artesanal."
```

### Fast Processing Configuration
```python
whisper_model = "small"
whisper_temperature = 0.0
whisper_fp16 = True
whisper_compression_ratio_threshold = 2.4
whisper_logprob_threshold = -1.0
whisper_no_speech_threshold = 0.6
whisper_condition_on_previous_text = False
whisper_initial_prompt = "Audio sobre cerveza."
```

### Balanced Configuration (Recommended)
```python
whisper_model = "medium"
whisper_temperature = 0.0
whisper_fp16 = False
whisper_compression_ratio_threshold = 2.4
whisper_logprob_threshold = -1.0
whisper_no_speech_threshold = 0.6
whisper_condition_on_previous_text = True
whisper_initial_prompt = "Este es un audio sobre cerveza y técnicas de elaboración de cerveza artesanal."
```

## Monitoring and Evaluation

### 1. Quality Metrics
- Word Error Rate (WER)
- Character Error Rate (CER)
- Confidence scores
- Processing time per minute of audio

### 2. Logging
```python
import logging

logging.info(f"Transcribing {filename}")
logging.info(f"Model: {whisper_model}")
logging.info(f"Audio duration: {duration} seconds")
logging.info(f"Processing time: {processing_time} seconds")
logging.info(f"Words transcribed: {word_count}")
logging.info(f"Average confidence: {avg_confidence}")
```

This guide should help you achieve the best possible Spanish transcription results with Whisper for your brewing content. 