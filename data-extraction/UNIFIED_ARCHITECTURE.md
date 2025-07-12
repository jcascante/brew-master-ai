# 🏗️ Unified Data Extraction Architecture

## 🎯 **Goal: Single, Complete Implementation**

Consolidate all functionality into a clean, unified architecture with:
- **One main CLI** - `brew_master.py`
- **One processing engine** - `processor.py`
- **One configuration system** - `config.py`
- **One test suite** - `tests/`
- **One documentation** - `README.md`

---

## 📁 **Proposed File Structure**

```
data-extraction/
├── 📄 brew_master.py              # Main CLI application (unified)
├── 📄 processor.py                # Core processing engine (unified)
├── 📄 config.py                   # Configuration system (unified)
├── 📄 validator.py                # Data validation utilities
├── 📄 config.yaml                 # Default configuration
├── 📄 requirements.txt            # Dependencies
├── 📄 README.md                   # Complete documentation
├── 📁 tests/                      # Unified test suite
│   ├── test_processor.py
│   ├── test_config.py
│   ├── test_validation.py
│   └── test_integration.py
├── 📁 examples/                   # Example scripts
│   ├── basic_pipeline.py
│   ├── custom_config.py
│   └── production_setup.py
└── 📁 docs/                       # Documentation
    ├── CLI_REFERENCE.md
    ├── CONFIGURATION.md
    └── API_REFERENCE.md
```

---

## 🔧 **Core Components**

### 1. **`brew_master.py`** - Main CLI Application
**Purpose:** Single entry point for all data processing operations

**Features:**
- Complete pipeline: audio extraction → transcription → embeddings
- Config management with YAML + CLI overrides
- Progress tracking and detailed reporting
- Error handling and recovery
- Validation and quality assessment
- Smart config selection
- Cleanup and deduplication

**Commands:**
```bash
# Complete pipeline
brew_master.py process --input videos/ --output embeddings/

# Individual stages
brew_master.py extract-audio --input videos/ --output audio/
brew_master.py transcribe --input audio/ --output transcripts/
brew_master.py create-embeddings --input transcripts/ --config video_transcript

# Configuration
brew_master.py config --list
brew_master.py config --show
brew_master.py config --validate

# Validation
brew_master.py validate --input transcripts/ --report quality_report.html

# Cleanup
brew_master.py cleanup --remove-orphaned
```

### 2. **`processor.py`** - Core Processing Engine
**Purpose:** Unified processing engine with all advanced features

**Classes:**
```python
class BrewMasterProcessor:
    """Main processing engine with all features"""
    
    def __init__(self, config: Config):
        self.config = config
        self.validator = DataValidator(config)
        self.chunker = TextChunker(config)
        self.metadata_enricher = MetadataEnricher()
        self.qdrant_client = QdrantClient()
    
    # Audio/Video processing
    def extract_audio(self, input_dir: str, output_dir: str) -> ProcessingResult
    def transcribe_audio(self, input_dir: str, output_dir: str) -> ProcessingResult
    
    # Presentation processing
    def extract_images(self, input_dir: str, output_dir: str) -> ProcessingResult
    def ocr_images(self, input_dir: str, output_dir: str) -> ProcessingResult
    
    # Text processing
    def process_text(self, input_dir: str, content_type: str) -> ProcessingResult
    def create_embeddings(self, input_dir: str, config_name: str) -> ProcessingResult
    
    # Advanced features
    def cleanup_orphaned_chunks(self, data_dirs: List[str]) -> CleanupResult
    def get_smart_config(self, content_type: str) -> str
    def should_process_file(self, file_path: str, config_name: str) -> bool
```

### 3. **`config.py`** - Unified Configuration System
**Purpose:** Single configuration system with all features

**Classes:**
```python
@dataclass
class Config:
    """Unified configuration with all settings"""
    
    # Directories
    input_dirs: Dict[str, str]
    output_dirs: Dict[str, str]
    
    # Processing settings
    processing: ProcessingConfig
    validation: ValidationConfig
    cleanup: CleanupConfig
    
    # Advanced features
    smart_config: bool = True
    deduplication: bool = True
    progress_tracking: bool = True

class ConfigManager:
    """Configuration management with YAML + CLI overrides"""
    
    def load_config(self, yaml_file: str, cli_args: Dict) -> Config
    def validate_config(self, config: Config) -> ValidationResult
    def save_config(self, config: Config, file_path: str)
    def list_presets(self) -> List[str]
    def get_preset(self, name: str) -> Config
```

---

## 🔄 **Migration Strategy**

### **Phase 1: Core Consolidation**
1. **Create `processor.py`** - Merge all processing logic
2. **Create `config.py`** - Unify configuration system
3. **Create `brew_master.py`** - Single CLI application
4. **Test core functionality**

### **Phase 2: Feature Integration**
1. **Integrate cleanup features** from `enhanced_processor_with_cleanup.py`
2. **Integrate smart config selection**
3. **Integrate progress tracking** from `enhanced_main.py`
4. **Integrate validation features** from `data_validator.py`

### **Phase 3: Testing & Documentation**
1. **Create unified test suite**
2. **Create comprehensive documentation**
3. **Create example scripts**
4. **Validate all functionality**

### **Phase 4: Cleanup**
1. **Remove deprecated files**
2. **Update imports and references**
3. **Update documentation**
4. **Final testing**

---

## 📋 **File Migration Plan**

### **Files to Keep (Consolidated)**
- ✅ `config.yaml` → Keep as default config
- ✅ `requirements.txt` → Keep and update
- ✅ `data_validator.py` → Merge into `validator.py`

### **Files to Merge**
- 🔄 `enhanced_main.py` + `main.py` → `brew_master.py`
- 🔄 `enhanced_processor.py` + `enhanced_processor_with_cleanup.py` → `processor.py`
- 🔄 `config_loader.py` + `chunking_configs.py` → `config.py`

### **Files to Remove**
- ❌ `main.py` → Legacy, functionality in `brew_master.py`
- ❌ `enhanced_main.py` → Merged into `brew_master.py`
- ❌ `enhanced_processor.py` → Merged into `processor.py`
- ❌ `enhanced_processor_with_cleanup.py` → Merged into `processor.py`
- ❌ `config_loader.py` → Merged into `config.py`
- ❌ `chunking_configs.py` → Merged into `config.py`
- ❌ `run_all_pipelines.py` → Functionality in `brew_master.py`
- ❌ `example_with_config.py` → Move to `examples/`
- ❌ `test_*.py` → Consolidate into `tests/`

### **Files to Consolidate**
- 📁 `test_*.py` → `tests/test_*.py`
- 📁 `example_*.py` → `examples/example_*.py`
- 📁 `README*.md` → Single `README.md`

---

## 🎯 **Benefits of Unified Architecture**

### **For Users:**
- ✅ **Single entry point** - `brew_master.py` for everything
- ✅ **Consistent interface** - Same CLI across all operations
- ✅ **Better documentation** - One comprehensive README
- ✅ **Easier installation** - Single requirements.txt

### **For Developers:**
- ✅ **No duplication** - Single implementation of each feature
- ✅ **Easier maintenance** - One place to update each feature
- ✅ **Better testing** - Unified test suite
- ✅ **Cleaner codebase** - Organized, modular structure

### **For Production:**
- ✅ **Reliable processing** - All advanced features in one place
- ✅ **Better error handling** - Unified error management
- ✅ **Comprehensive logging** - Consistent logging across all operations
- ✅ **Easy deployment** - Single application to deploy

---

## 🚀 **Implementation Plan**

### **Step 1: Create Core Files**
1. Create `processor.py` with unified processing engine
2. Create `config.py` with unified configuration system
3. Create `brew_master.py` with unified CLI

### **Step 2: Migrate Features**
1. Migrate audio/transcription from `enhanced_main.py`
2. Migrate text processing from `enhanced_processor.py`
3. Migrate cleanup features from `enhanced_processor_with_cleanup.py`
4. Migrate config management from `config_loader.py`

### **Step 3: Create Tests**
1. Create unified test suite in `tests/`
2. Test all functionality
3. Ensure backward compatibility

### **Step 4: Update Documentation**
1. Create comprehensive README.md
2. Create API documentation
3. Create example scripts

### **Step 5: Cleanup**
1. Remove deprecated files
2. Update any external references
3. Final validation

---

## 🎉 **Expected Outcome**

After consolidation, you'll have:

- **One main application** - `brew_master.py`
- **One processing engine** - `processor.py`
- **One configuration system** - `config.py`
- **One test suite** - `tests/`
- **One documentation** - `README.md`

**Result:** Clean, maintainable, feature-complete data extraction module! 🍺 