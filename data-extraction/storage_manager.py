#!/usr/bin/env python3
"""
Storage manager for Brew Master AI data processing.
Handles EBS + S3 workflow for both local and production environments.
"""

import os
import boto3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, config):
        self.config = config
        self.environment = self._detect_environment()
        self.storage_config = self._get_storage_config()
        self.s3_client = self._init_s3_client()
        self._ensure_directories()
    
    def _detect_environment(self):
        """Detect if running locally or on EC2"""
        if os.path.exists('/sys/hypervisor/uuid'):
            return 'production'
        return 'local'
    
    def _get_storage_config(self):
        """Get storage configuration based on environment"""
        if self.environment == 'production':
            return {
                'local_data_dir': '/mnt/data',  # EBS mount point
                'temp_dir': '/mnt/data/temp',
                'models_dir': '/mnt/data/models',
                'input_dir': '/mnt/data/input',  # Local input directory for production
                's3_bucket': self.config.get('s3_bucket', 'brew-master-ai-data'),
                's3_input_prefix': 'audio/input/',
                's3_output_prefix': 'transcripts/',
                's3_processed_prefix': 'audio/processed/'
            }
        else:
            return {
                'local_data_dir': './data',
                'temp_dir': './data/temp',
                'models_dir': './data/models',
                'input_dir': './data/input',  # Local input directory for local development
                's3_bucket': self.config.get('s3_bucket', 'brew-master-ai-data'),
                's3_input_prefix': 'audio/input/',
                's3_output_prefix': 'transcripts/',
                's3_processed_prefix': 'audio/processed/'
            }
    
    def _init_s3_client(self):
        """Initialize S3 client"""
        try:
            return boto3.client('s3')
        except Exception as e:
            logger.warning(f"Could not initialize S3 client: {e}")
            return None
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for dir_path in [self.storage_config['local_data_dir'], 
                        self.storage_config['temp_dir'], 
                        self.storage_config['models_dir'],
                        self.storage_config['input_dir']]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_file_paths(self, filename: str) -> Dict[str, str]:
        """Get local and S3 paths for a file"""
        return {
            'local_input': os.path.join(self.storage_config['temp_dir'], filename),
            'local_output': os.path.join(self.storage_config['temp_dir'], f"{filename}.txt"),
            'local_source': os.path.join(self.storage_config['input_dir'], filename),  # Source file location
            's3_input': f"{self.storage_config['s3_input_prefix']}{filename}",
            's3_output': f"{self.storage_config['s3_output_prefix']}{filename}.txt",
            's3_processed': f"{self.storage_config['s3_processed_prefix']}{filename}"
        }
    
    def download_from_s3(self, s3_key: str, local_path: str) -> bool:
        """Download file from S3 to local storage"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        try:
            logger.info(f"Downloading {s3_key} to {local_path}")
            self.s3_client.download_file(self.storage_config['s3_bucket'], s3_key, local_path)
            return True
        except ClientError as e:
            logger.error(f"Failed to download {s3_key}: {e}")
            return False
    
    def upload_to_s3(self, local_path: str, s3_key: str) -> bool:
        """Upload file from local storage to S3"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        try:
            logger.info(f"Uploading {local_path} to {s3_key}")
            self.s3_client.upload_file(local_path, self.storage_config['s3_bucket'], s3_key)
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def list_s3_files(self, prefix: str) -> List[str]:
        """List files in S3 with given prefix"""
        if not self.s3_client:
            logger.error("S3 client not available")
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.storage_config['s3_bucket'],
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logger.error(f"Failed to list S3 files: {e}")
            return []
    
    def list_local_files(self, directory: str = None) -> List[str]:
        """List files in local input directory"""
        if directory is None:
            directory = self.storage_config['input_dir']
        
        try:
            files = []
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    # Check if it's an audio file
                    if self._is_audio_file(file):
                        files.append(file)
            return files
        except Exception as e:
            logger.error(f"Failed to list local files: {e}")
            return []
    
    def _is_audio_file(self, filename: str) -> bool:
        """Check if file is an audio file"""
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']
        return any(filename.lower().endswith(ext) for ext in audio_extensions)
    
    def process_audio_file(self, filename: str) -> bool:
        """
        Main workflow: 
        - Local: Copy from input dir → Process → Upload to S3
        - Production: Download from S3 → Process → Upload to S3
        """
        paths = self.get_file_paths(filename)
        
        if self.environment == 'local':
            # Local workflow: files are already on disk
            logger.info(f"Local mode: Processing {filename} from local input directory")
            
            # Step 1: Copy from input directory to temp directory
            if not os.path.exists(paths['local_source']):
                logger.error(f"Source file not found: {paths['local_source']}")
                return False
            
            import shutil
            shutil.copy2(paths['local_source'], paths['local_input'])
            logger.info(f"Copied {filename} to temp directory")
            
        else:
            # Production workflow: download from S3
            logger.info(f"Production mode: Downloading {filename} from S3")
            if not self.download_from_s3(paths['s3_input'], paths['local_input']):
                return False
        
        # Step 2: Process with Whisper (this will be done by your existing code)
        logger.info(f"Step 2: Processing {filename} with Whisper")
        # Your Whisper processing code will use paths['local_input'] and paths['local_output']
        
        # Step 3: Upload transcript to S3 (both local and production)
        logger.info(f"Step 3: Uploading transcript for {filename}")
        if os.path.exists(paths['local_output']):
            if not self.upload_to_s3(paths['local_output'], paths['s3_output']):
                return False
        
        # Step 4: Move processed file to processed folder in S3 (both local and production)
        logger.info(f"Step 4: Moving {filename} to processed folder")
        if not self.upload_to_s3(paths['local_input'], paths['s3_processed']):
            return False
        
        # Step 5: Cleanup local files (optional)
        logger.info(f"Step 5: Cleaning up local files")
        self._cleanup_local_files(paths)
        
        return True
    
    def process_all_local_files(self) -> List[str]:
        """Process all audio files in the local input directory"""
        files = self.list_local_files()
        processed_files = []
        
        for filename in files:
            logger.info(f"Processing local file: {filename}")
            if self.process_audio_file(filename):
                processed_files.append(filename)
            else:
                logger.error(f"Failed to process {filename}")
        
        return processed_files
    
    def _cleanup_local_files(self, paths: Dict[str, str]):
        """Clean up local temporary files"""
        for path_key in ['local_input', 'local_output']:
            if os.path.exists(paths[path_key]):
                try:
                    os.remove(paths[path_key])
                    logger.info(f"Cleaned up {paths[path_key]}")
                except Exception as e:
                    logger.warning(f"Could not clean up {paths[path_key]}: {e}")
    
    def get_pending_files(self) -> List[str]:
        """Get list of files pending processing"""
        if self.environment == 'local':
            # For local mode, return files in input directory
            return self.list_local_files()
        else:
            # For production mode, check S3
            input_files = self.list_s3_files(self.storage_config['s3_input_prefix'])
            processed_files = self.list_s3_files(self.storage_config['s3_processed_prefix'])
            
            # Extract filenames
            input_filenames = {os.path.basename(f) for f in input_files}
            processed_filenames = {os.path.basename(f) for f in processed_files}
            
            # Return files that are in input but not in processed
            return list(input_filenames - processed_filenames) 