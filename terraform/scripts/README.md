# 🛠️ Brew Master AI - Management Scripts

Convenient scripts to manage your on-demand processing infrastructure.

## 📁 Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `start-processing.sh` | 🚀 Start processing job | `./scripts/start-processing.sh` |
| `stop-processing.sh` | 🛑 Stop processing job | `./scripts/stop-processing.sh` |
| `check-status.sh` | 📊 Check system status | `./scripts/check-status.sh` |
| `upload-files.sh` | 📤 Upload files to S3 | `./scripts/upload-files.sh files...` |

## 🚀 **start-processing.sh**

**Creates ephemeral infrastructure and starts processing**

### Features:
- ✅ Validates persistent infrastructure exists
- ✅ Checks for input files in S3
- ✅ Deploys EC2 spot instance + EBS volume
- ✅ Waits for instance to be ready
- ✅ Shows connection information

### Usage:
```bash
./scripts/start-processing.sh
```

### What it does:
1. Checks persistent infrastructure (creates if missing)
2. Validates S3 bucket and input files
3. Deploys ephemeral infrastructure (EC2 + EBS)
4. Waits for instance setup completion
5. Shows SSH access and monitoring commands

### Example output:
```
🍺 Brew Master AI - Starting Processing Job
============================================
✅ Persistent infrastructure exists
📦 Using S3 bucket: brew-master-ai-data-abc12345
✅ Found 3 files in S3 input directory
🚀 Deploying ephemeral infrastructure...
✅ Instance is ready for SSH
🎉 Processing job started successfully!
```

## 🛑 **stop-processing.sh**

**Safely stops processing and destroys ephemeral infrastructure**

### Features:
- ✅ Checks for active processing (warns if running)
- ✅ Backs up temporary data to S3
- ✅ Shows results summary
- ✅ Destroys ephemeral infrastructure
- ✅ Calculates cost savings

### Usage:
```bash
./scripts/stop-processing.sh
```

### What it does:
1. Checks if processing is active (warns user)
2. Backs up any temp data to S3
3. Shows results summary
4. Confirms destruction with user
5. Destroys ephemeral infrastructure
6. Shows cost savings achieved

### Example output:
```
🍺 Brew Master AI - Stopping Processing Job
============================================
✅ No active processing detected
📊 Results Summary: 5 processed files
💰 Session cost (2.3 hours): $5.75
🎉 Processing job stopped successfully!
```

## 📊 **check-status.sh**

**Monitor infrastructure and processing status**

### Features:
- ✅ Infrastructure status (persistent + ephemeral)
- ✅ S3 storage analysis
- ✅ EC2 processing status
- ✅ Cost information
- ✅ Recommended actions
- ✅ Watch mode for continuous monitoring

### Usage:
```bash
# Single check
./scripts/check-status.sh

# Continuous monitoring
./scripts/check-status.sh --watch
```

### What it shows:
- Infrastructure status (active/inactive)
- S3 file counts (input/processed/logs)
- EC2 system metrics (CPU/memory/disk)
- Active processes and recent logs
- Current costs and runtime
- Next recommended actions

### Example output:
```
🍺 Brew Master AI - Status Check
=================================
🏗️  Infrastructure Status:
   ✅ Persistent infrastructure: Active
   ✅ Ephemeral infrastructure: Active
☁️  S3 Storage Status:
   📥 Input files: 3
   📤 Processed files: 1
🖥️  EC2 Processing Status:
   ✅ Instance setup: Complete
   🔄 Active Processes: Processing active (2 processes)
💰 Cost Information:
   ⏱️  Runtime: 1.2 hours
   💵 Estimated cost: $3.00
```

## 📤 **upload-files.sh**

**Upload files to S3 for processing**

### Features:
- ✅ File type validation
- ✅ Size calculation and cost estimation
- ✅ Progress tracking
- ✅ Directory upload support
- ✅ Dry-run mode

### Usage:
```bash
# Upload specific files
./scripts/upload-files.sh video1.mp4 video2.mp4

# Upload entire directory
./scripts/upload-files.sh --dir /path/to/videos/

# Upload directory recursively
./scripts/upload-files.sh --recursive /path/to/project/

# Preview without uploading
./scripts/upload-files.sh --dry-run *.mp4
```

### Supported file types:
- **Videos:** mp4, avi, mov, mkv
- **Audio:** wav, mp3, m4a  
- **Presentations:** pptx, ppt

### Example output:
```
🍺 Brew Master AI - File Upload
===============================
📋 Validating file types...
   ✅ Valid: video1.mp4 (mp4)
   ✅ Valid: presentation.pptx (pptx)
📊 Upload Analysis:
   📦 Total size: 1.250 GB
   💰 Monthly storage cost: $0.0288
   ⏱️  Estimated upload time: 2.1 minutes
📤 Uploading files to S3...
🎉 Upload Complete!
```

## 🔄 **Complete Workflow**

### 1. Upload Files
```bash
./scripts/upload-files.sh my-video.mp4 presentation.pptx
```

### 2. Start Processing
```bash
./scripts/start-processing.sh
```

### 3. Monitor Progress
```bash
# Check status
./scripts/check-status.sh

# Watch continuously
./scripts/check-status.sh --watch

# SSH to instance
ssh -i brew-master-ai-key.pem ubuntu@IP
tail -f /mnt/temp-data/logs/brew_master.log
```

### 4. Get Results
```bash
# List results
aws s3 ls s3://BUCKET-NAME/processed/

# Download results
aws s3 sync s3://BUCKET-NAME/processed/ ./results/
```

### 5. Stop Processing
```bash
./scripts/stop-processing.sh
```

## 💡 **Tips & Best Practices**

### Cost Optimization:
- ✅ Always run `stop-processing.sh` when done
- ✅ Use `check-status.sh` to monitor costs
- ✅ Upload files in batches to maximize instance utilization
- ✅ Use spot instances (already configured)

### Monitoring:
- ✅ Use `--watch` mode during long processing jobs
- ✅ Check S3 logs for detailed processing history
- ✅ Monitor CloudWatch for detailed metrics

### Troubleshooting:
- ✅ Check `check-status.sh` first for issues
- ✅ SSH to instance and check `/mnt/temp-data/logs/`
- ✅ Verify S3 permissions if upload fails
- ✅ Use `terraform plan` to validate infrastructure

### File Management:
- ✅ Use descriptive filenames for easy identification
- ✅ Process files in batches of similar types
- ✅ Clean up S3 regularly (lifecycle policies help)
- ✅ Download results promptly to local storage

## 🔧 **Advanced Usage**

### Custom Processing:
```bash
# SSH to instance
ssh -i brew-master-ai-key.pem ubuntu@IP

# Run custom processing
cd /home/ubuntu/brew-master-ai
source venv/bin/activate
python3 -c "from data_extraction.brew_master import BrewMasterCLI; cli = BrewMasterCLI(); cli.process_pipeline()"
```

### Direct Terraform Commands:
```bash
# Deploy only persistent
terraform apply -target=module.persistent

# Deploy only ephemeral  
terraform apply -target=module.ephemeral

# Destroy only ephemeral
terraform destroy -target=module.ephemeral
```

### Manual S3 Management:
```bash
# List all files
aws s3 ls s3://BUCKET-NAME/ --recursive

# Copy specific files
aws s3 cp s3://BUCKET-NAME/processed/result.txt ./

# Clean up input files
aws s3 rm s3://BUCKET-NAME/input/ --recursive
```

---

**🍺 Ready to process your brewing data efficiently and cost-effectively!**