#!/bin/bash
# Bootstrap script for Brew Master AI - Downloads and runs full setup

set -e

# Configuration from Terraform
S3_BUCKET_NAME="${s3_bucket_name}"
GITHUB_REPO="https://github.com/jcascante/brew-master-ai.git"

echo "🚀 Bootstrapping EC2 instance for Brew Master AI..."
echo "📦 S3 Bucket: $S3_BUCKET_NAME"

# Update system
sudo apt update && sudo apt install -y git curl

# Clone repository to get full setup script
cd /home/ubuntu
git clone $GITHUB_REPO || (cd brew-master-ai && git pull)

# Create full setup script with S3 bucket name
cat > /home/ubuntu/brew-master-ai/full_setup.sh << 'FULLSETUP'
#!/bin/bash
# Full EC2 setup script for Brew Master AI

set -e

S3_BUCKET_NAME="__S3_BUCKET_PLACEHOLDER__"
echo "🚀 Running full setup for Brew Master AI..."
echo "📦 S3 Bucket: $S3_BUCKET_NAME"

# Install essential packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl wget unzip ffmpeg tesseract-ocr build-essential awscli docker.io

# Setup Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Setup storage
sudo mkdir -p /mnt/temp-data
sudo chown ubuntu:ubuntu /mnt/temp-data

# Mount EBS volume
if ! mountpoint -q /mnt/temp-data; then
    DEVICE=""
    for dev in xvdf sdf nvme1n1; do
        if [ -e /dev/$dev ]; then
            DEVICE="/dev/$dev"
            break
        fi
    done
    
    if [ -n "$DEVICE" ]; then
        if ! sudo blkid $DEVICE; then
            sudo mkfs.ext4 $DEVICE
        fi
        sudo mount $DEVICE /mnt/temp-data
        sudo chown ubuntu:ubuntu /mnt/temp-data
        echo "$DEVICE /mnt/temp-data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
        echo "✅ EBS volume mounted"
    else
        mkdir -p /home/ubuntu/temp-data
        ln -sf /home/ubuntu/temp-data /mnt/temp-data
    fi
fi

# Create directories
mkdir -p /mnt/temp-data/{input,output,temp,logs,models}

# Setup Python environment
cd /home/ubuntu/brew-master-ai
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd data-extraction
pip install --upgrade pip
pip install -r requirements.txt
pip install boto3 awscli pyyaml

# Configure AWS
aws configure set region $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/.$//')
aws configure set output json

# Test S3 access
if aws s3 ls s3://$S3_BUCKET_NAME/ > /dev/null 2>&1; then
    echo "✅ S3 access confirmed"
else
    echo "❌ S3 access failed"
fi

# Create EC2 config
cat > config_ec2.yaml << EOFCONFIG
s3_bucket: "$S3_BUCKET_NAME"
s3_input_prefix: "input/"
s3_output_prefix: "processed/"
whisper_model: "base"
language: "es"
device: "cpu"
max_workers: 4
local_temp_dir: "/mnt/temp-data/temp"
local_input_dir: "/mnt/temp-data/input"
local_output_dir: "/mnt/temp-data/output"
model_cache_dir: "/mnt/temp-data/models"
log_file: "/mnt/temp-data/logs/brew_master.log"
cleanup_temp_files: true
EOFCONFIG

# Create processing scripts
cat > /home/ubuntu/start_processing.sh << 'EOFSTART'
#!/bin/bash
set -e
echo "🍺 Starting processing..."
cd /home/ubuntu/brew-master-ai
source venv/bin/activate
python3 -c "
import boto3, sys, os
from pathlib import Path
sys.path.append('data-extraction')
from brew_master import BrewMasterCLI

# Simple S3 processing
s3 = boto3.client('s3')
bucket = 'BUCKET_PLACEHOLDER'

# Download files
os.makedirs('/mnt/temp-data/input', exist_ok=True)
try:
    objects = s3.list_objects_v2(Bucket=bucket, Prefix='input/')
    if 'Contents' in objects:
        for obj in objects['Contents']:
            if not obj['Key'].endswith('/'):
                local_file = f\"/mnt/temp-data/input/{Path(obj['Key']).name}\"
                s3.download_file(bucket, obj['Key'], local_file)
                print(f'Downloaded: {obj[\"Key\"]}')
    
    # Process if files exist
    if os.listdir('/mnt/temp-data/input'):
        cli = BrewMasterCLI()
        cli.setup({'videos_dir': '/mnt/temp-data/input', 'output_dir': '/mnt/temp-data/output'})
        cli.process_pipeline('/mnt/temp-data/input', '/mnt/temp-data/output')
        
        # Upload results
        os.makedirs('/mnt/temp-data/output', exist_ok=True)
        for file in Path('/mnt/temp-data/output').glob('**/*'):
            if file.is_file():
                s3.upload_file(str(file), bucket, f'processed/{file.name}')
                print(f'Uploaded: {file.name}')
    else:
        print('No files to process')
except Exception as e:
    print(f'Error: {e}')
"
echo "✅ Processing completed"
EOFSTART

# Replace bucket placeholder
sed -i "s/BUCKET_PLACEHOLDER/$S3_BUCKET_NAME/g" /home/ubuntu/start_processing.sh
chmod +x /home/ubuntu/start_processing.sh

# Create status script
cat > /home/ubuntu/check_status.sh << 'EOFSTATUS'
#!/bin/bash
echo "🍺 Brew Master AI Status"
echo "S3 Access: $(aws s3 ls s3://BUCKET_PLACEHOLDER/ > /dev/null 2>&1 && echo '✅ OK' || echo '❌ Failed')"
echo "Disk: $(df -h /mnt/temp-data | tail -1 | awk '{print $4 " available"}')"
echo "Recent logs:"
tail -5 /mnt/temp-data/logs/brew_master.log 2>/dev/null || echo "No logs yet"
EOFSTATUS

sed -i "s/BUCKET_PLACEHOLDER/$S3_BUCKET_NAME/g" /home/ubuntu/check_status.sh
chmod +x /home/ubuntu/check_status.sh

# Mark setup complete
touch /home/ubuntu/setup_complete.flag
echo "🎉 Full setup completed!"
FULLSETUP

# Replace placeholder and run full setup
sed -i "s/__S3_BUCKET_PLACEHOLDER__/$S3_BUCKET_NAME/g" /home/ubuntu/brew-master-ai/full_setup.sh
chmod +x /home/ubuntu/brew-master-ai/full_setup.sh

# Run full setup in background (avoid user_data timeout)
nohup /home/ubuntu/brew-master-ai/full_setup.sh > /var/log/full_setup.log 2>&1 &

echo "✅ Bootstrap completed. Full setup running in background." 