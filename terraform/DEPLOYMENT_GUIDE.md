# 🚀 Brew Master AI - Cost-Optimized Deployment Guide

## 💰 Cost Optimization Summary

**Previous Setup:**
- 100GB EBS volume: ~$8/month (always attached)
- Total estimated cost: ~$90-150/month

**Optimized Setup:**
- 20GB EBS volume: ~$1.6/month (temporary processing only)
- S3 storage: ~$0.023/GB/month (pay per use)
- **Estimated savings: 75% on storage costs**

## 🏗️ Infrastructure Changes

### ✅ Completed Optimizations

1. **EBS Volume Reduction**: 100GB → 20GB (temp processing only)
2. **S3 Integration**: Added S3 bucket with lifecycle policies
3. **IAM Setup**: EC2 instance profile for S3 access
4. **Enhanced Setup Script**: Full data-extraction pipeline deployment
5. **Automated Processing**: S3 → EC2 → S3 workflow

### 🏛️ New Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   S3 Storage    │    │   EC2 Instance  │    │   S3 Results    │
│                 │    │                 │    │                 │
│ • Videos        │───▶│ • 20GB EBS      │───▶│ • Transcripts   │
│ • Documents     │    │ • Temp Process  │    │ • Embeddings    │
│ • Lifecycle     │    │ • Auto Cleanup  │    │ • Reports       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Deployment Steps

### 1. Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

### 2. Get Connection Info

```bash
# Get outputs
terraform output

# Copy private key for SSH access
terraform output -raw private_key > brew-master-ai-key.pem
chmod 600 brew-master-ai-key.pem

# Get connection command
terraform output ssh_command
```

### 3. Connect to Instance

```bash
# SSH to instance (replace with your IP)
ssh -i brew-master-ai-key.pem ubuntu@<PUBLIC_IP>

# Check setup status
~/check_status.sh
```

## 📦 S3 Workflow

### Upload Files for Processing

```bash
# Upload videos/documents to S3
aws s3 cp your-video.mp4 s3://YOUR-BUCKET-NAME/input/
aws s3 cp your-document.pptx s3://YOUR-BUCKET-NAME/input/

# List uploaded files
aws s3 ls s3://YOUR-BUCKET-NAME/input/
```

### Start Processing

```bash
# On EC2 instance
~/start_processing.sh

# Or manually
cd /home/ubuntu/brew-master-ai
source venv/bin/activate
python3 process_s3.py
```

### Get Results

```bash
# Check results in S3
aws s3 ls s3://YOUR-BUCKET-NAME/processed/

# Download results
aws s3 sync s3://YOUR-BUCKET-NAME/processed/ ./results/
```

## 🔧 Management Commands

### On EC2 Instance

```bash
# Check system status
~/check_status.sh

# View processing logs
tail -f /mnt/temp-data/logs/brew_master.log

# Start processing manually
~/start_processing.sh

# Check disk usage
df -h /mnt/temp-data

# View S3 bucket contents
aws s3 ls s3://YOUR-BUCKET-NAME/ --recursive
```

### From Local Machine

```bash
# Get S3 bucket name
terraform output s3_bucket_name

# Upload files
aws s3 cp file.mp4 s3://$(terraform output -raw s3_bucket_name)/input/

# Check processing status via SSH
ssh -i brew-master-ai-key.pem ubuntu@$(terraform output -raw public_ip) "~/check_status.sh"

# Destroy infrastructure when done
terraform destroy
```

## 📊 Monitoring & Logs

### CloudWatch Integration

The setup script creates CloudWatch configuration for:
- **CPU usage**
- **Memory usage** 
- **Disk usage**
- **Application logs**

### Log Locations

- **Application logs**: `/mnt/temp-data/logs/brew_master.log`
- **System logs**: `journalctl -u brew-master-ai.service`
- **Setup logs**: `/var/log/cloud-init-output.log`

## 🛠️ Troubleshooting

### Common Issues

1. **S3 Access Denied**
   ```bash
   # Check IAM instance profile
   aws sts get-caller-identity
   
   # Test S3 access
   aws s3 ls s3://YOUR-BUCKET-NAME/
   ```

2. **EBS Volume Not Mounted**
   ```bash
   # Check mount status
   lsblk
   df -h
   
   # Manual mount if needed
   sudo mount /dev/xvdf /mnt/temp-data
   ```

3. **Processing Failures**
   ```bash
   # Check logs
   tail -100 /mnt/temp-data/logs/brew_master.log
   
   # Check Python environment
   source /home/ubuntu/brew-master-ai/venv/bin/activate
   pip list
   ```

### Debug Mode

```bash
# Run processing with debug output
cd /home/ubuntu/brew-master-ai
source venv/bin/activate
python3 -u process_s3.py 2>&1 | tee debug.log
```

## 💡 Cost Optimization Tips

1. **Use Spot Instances**: Already configured (50-70% savings)
2. **Stop Instance When Not Processing**: 
   ```bash
   aws ec2 stop-instances --instance-ids $(terraform output -raw instance_id)
   ```
3. **S3 Lifecycle Policies**: Automatically move old files to cheaper storage
4. **Cleanup Temp Files**: Automatic cleanup after processing
5. **Destroy Infrastructure**: When not needed long-term

## 🔄 Automated Processing

### Systemd Service

A systemd service is installed for automatic processing:

```bash
# Start service
sudo systemctl start brew-master-ai.service

# View service status
sudo systemctl status brew-master-ai.service

# View service logs
journalctl -u brew-master-ai.service -f
```

### Scheduled Processing

To run processing on a schedule:

```bash
# Add to crontab
crontab -e

# Example: Process every hour
0 * * * * /home/ubuntu/start_processing.sh >> /mnt/temp-data/logs/cron.log 2>&1
```

## 📈 Scaling Considerations

- **Larger instances**: Change `instance_type` in `variables.tf`
- **Multiple instances**: Consider AWS Batch for parallel processing
- **GPU acceleration**: Use GPU instances for faster Whisper processing
- **Lambda triggers**: Use S3 event triggers to start processing automatically

## 🔒 Security Notes

- EC2 instance uses IAM roles (no API keys stored)
- S3 bucket has encryption enabled
- EBS volumes are encrypted
- Security group allows SSH from anywhere (consider restricting)

---

**Ready to deploy!** 🍺 Your cost-optimized Brew Master AI infrastructure is configured and ready for processing.