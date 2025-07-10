# 🚀 Brew Master AI: Full Data Pipeline Runner

This script runs the **entire data extraction, validation, and embedding pipeline** for Brew Master AI, from raw videos and presentations to a fully populated vector database with rich metadata.

## Usage

```bash
cd data-extraction
python run_all_pipelines.py --config <preset>
```

- `<preset>`: Choose a chunking/quality configuration (see below for options)
- Omit `--config` to use the default (`general_brewing`)

### Example
```bash
python run_all_pipelines.py --config video_transcript
python run_all_pipelines.py --config balanced
```

### List All Configurations
```bash
python run_all_pipelines.py --list-configs
```

## What This Script Does

1. **Extracts audio** from all videos in `data/videos/`
2. **Transcribes audio** to text in `data/transcripts/`
3. **Extracts images** from presentations in `data/presentations/`
4. **Runs OCR** on images to produce `data/presentation_texts/`
5. **Validates** transcripts and OCR text (prints quality reports)
6. **Creates embeddings** for all valid text chunks using the chosen config
7. **Uploads** all chunks (with metadata) to the Qdrant vector database
8. **Prints a sample** of the resulting metadata for inspection

## Output

- **Quality reports** for transcripts and OCR text (printed to terminal)
- **Embeddings** uploaded to Qdrant with rich metadata
- **Sample metadata** for a random chunk (printed at the end)
- **Logs** for each pipeline step

## Configuration Presets

- `video_transcript` — For long-form video content
- `presentation_text` — For slide-based content
- `technical_brewing` — For technical brewing docs
- `general_brewing` — Balanced for most content (default)
- `recipe_content` — For preserving complete recipes
- `faq_content` — For Q&A style content
- `historical_content` — For narrative/historical docs
- `equipment_specs` — For technical specs
- `high_quality`, `balanced`, `fast_processing` — Quality/speed trade-offs

See `ENHANCED_README.md` for full details on each preset.

## Troubleshooting

- **Font warnings**: Matplotlib may print font cache warnings the first time; these are harmless.
- **Missing dependencies**: Make sure your virtual environment is activated and all requirements are installed:
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- **Qdrant not running**: Ensure your vector DB is up:
  ```bash
  cd ../vector-db
  docker compose up -d
  ```
- **No data found**: Make sure you have files in `data/videos/` and/or `data/presentations/`.
- **Custom chunking**: For advanced options, use `enhanced_main.py` directly.

## Next Steps

- Query your Qdrant vector DB with the backend RAG system
- Review quality reports for data issues
- Explore more options in `ENHANCED_README.md`

---

**Brew Master AI — End-to-end data pipeline, ready for production! 🍺** 