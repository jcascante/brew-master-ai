# Brew Master AI - Deployment Guide

This guide explains how to deploy and run the Brew Master AI data extraction pipeline using the EBS + S3 workflow.

## Architecture Overview

### Local Development
```
Local Input → Process → S3 (Output Only)
     ↓           ↓           ↓
Audio Files → Whisper → Transcripts
```

### Production (EC2)
```
S3 (Input) → EBS (Processing) → S3 (Output)
     ↓              ↓              ↓
Audio Files → Whisper Processing → Transcripts
```

## Prerequisites

### For Local Development
- Python 3.8+
- AWS CLI configured
- S3 bucket created
- Required Python packages (see requirements.txt)

### For Production (EC2)
- Terraform configuration deployed
- EC2 instance running with EBS volume
- S3 bucket with proper permissions

## Setup Instructions

### 1. Local Development Setup

```bash
# Clone the repository
cd data-extraction

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Create S3 bucket (if not exists)
aws s3 mb s3://brew-master-ai-data

# Create local directories
mkdir -p data/input data/temp data/models data/logs
```

### 2. Production (EC2) Setup

The EC2 instance is automatically configured via Terraform and the setup script.

```bash
# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# SSH into the instance
ssh -i id_rsa_<key-name> ubuntu@<public-ip>

# The setup script runs automatically, but you can re-run if needed:
sudo bash /var/lib/cloud/instances/*/user-data.txt
```

## Usage

### Local Development

```bash
# Place your audio files in the input directory
cp your_audio_file.mp3 data/input/

# Process a single file
python brew_master.py --file audio_file.mp3

# Process all files in the input directory
python brew_master.py --process-all

# Run with custom config
python brew_master.py --config custom_config.yaml
```

### Production (EC2)

```bash
# SSH into the instance
ssh -i terraform/id_rsa_<key-name> ubuntu@<public-ip>

# Navigate to data directory
cd /mnt/data

# Activate virtual environment
source venv/bin/activate

# Upload files to S3 (if not already there)
aws s3 cp audio_file.mp3 s3://brew-master-ai-data/audio/input/

# Run processing
python3 brew_master.py --process-all

# Or use the startup script
./start_processing.sh
```

## Workflow

### Local Development Workflow
1. **Place files in input directory:** Copy audio files to `./data/input/`
2. **Process files:** Run the processing script
3. **Upload results:** Transcripts are automatically uploaded to S3
4. **Cleanup:** Temporary files are cleaned up

### Production Workflow
1. **Upload to S3:** Upload audio files to S3 bucket
2. **Download to EBS:** Files are downloaded to EC2 for processing
3. **Process with Whisper:** Audio is transcribed
4. **Upload results:** Transcripts are uploaded back to S3
5. **Cleanup:** Local files are cleaned up

### 3. Retrieve Results
Download transcripts from S3:
```bash
aws s3 ls s3://brew-master-ai-data/transcripts/
aws s3 cp s3://brew-master-ai-data/transcripts/audio_file.mp3.txt ./
```

## Configuration

### Environment Detection
The system automatically detects the environment:
- **Local**: Uses `./data` directory, reads from local input folder
- **Production**: Uses `/mnt/data` directory (EBS volume), downloads from S3

### Configuration File
Edit `config.yaml` to customize:
- S3 bucket and prefixes
- Whisper model settings
- Processing parameters
- Logging configuration

## Monitoring

### Check Processing Status
```bash
# List pending files (local mode)
python brew_master.py --list-pending

# Check S3 contents
aws s3 ls s3://brew-master-ai-data/audio/input/
aws s3 ls s3://brew-master-ai-data/transcripts/
```

### View Logs
```bash
# Local
tail -f data/logs/brew_master.log

# Production
tail -f /mnt/data/logs/brew_master.log
```

## Cost Optimization

### Spot Instances
- Use Spot instances for 60-90% cost savings
- Set appropriate bid prices
- Handle interruptions gracefully

### Storage
- EBS for processing (fast access)
- S3 for long-term storage (cost-effective)
- Clean up temporary files

### Instance Types
- **c5.2xlarge**: Good balance of cost and performance
- **c5.4xlarge**: More power for larger workloads

## Troubleshooting

### Common Issues

1. **S3 Access Denied**
   - Check IAM permissions
   - Verify bucket name and region

2. **EBS Volume Not Mounted**
   - Check device name in setup script
   - Verify volume attachment

3. **Whisper Model Download Issues**
   - Check internet connectivity
   - Verify model cache directory permissions

4. **Spot Instance Interruption**
   - Use persistent EBS volumes
   - Implement checkpointing in your code

5. **Local Files Not Found**
   - Check that files are in the correct input directory
   - Verify file permissions

### Debug Commands
```bash
# Check EBS mount
df -h /mnt/data

# Check S3 connectivity
aws s3 ls s3://brew-master-ai-data

# Check Python environment
python3 -c "import whisper; print('Whisper OK')"

# Check disk space
du -sh /mnt/data/*

# List local input files
ls -la data/input/
```

## Security Considerations

1. **IAM Permissions**: Use least privilege principle
2. **EBS Encryption**: Enabled by default in Terraform
3. **SSH Keys**: Store securely, rotate regularly
4. **S3 Bucket**: Configure appropriate access policies

## Scaling

### Horizontal Scaling
- Deploy multiple EC2 instances
- Use S3 as shared storage
- Implement load balancing

### Vertical Scaling
- Use larger instance types
- Increase EBS volume size
- Optimize Whisper model size

## Support

For issues or questions:
1. Check the logs
2. Review configuration
3. Test locally first
4. Check AWS service status 