#!/bin/bash

# Brew Master AI Data Extraction Instance Setup Script
# This script sets up an EC2 instance for data extraction with GPU support

set -e

# Configuration variables
ENVIRONMENT="${environment}"
APP_NAME="${app_name}"
APP_VERSION="${app_version}"
VECTOR_DB_HOST="${vector_db_host}"
VECTOR_DB_PORT="${vector_db_port}"
ENABLE_GPU="${enable_gpu}"
GPU_DRIVER_URL="${gpu_driver_url}"
CUDA_VERSION="${cuda_version}"

# Logging setup
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting Brew Master AI Data Extraction instance setup..."

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install essential packages
echo "Installing essential packages..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    tesseract-ocr \
    tesseract-ocr-spa \
    ffmpeg \
    nginx \
    supervisor \
    htop \
    iotop \
    nvtop \
    awscli \
    jq

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# GPU Setup (if enabled)
if [ "$ENABLE_GPU" = "true" ]; then
    echo "Setting up GPU support..."
    
    # Install NVIDIA drivers
    apt-get install -y nvidia-driver-535 nvidia-utils-535
    
    # Install CUDA toolkit
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
    dpkg -i cuda-keyring_1.0-1_all.deb
    apt-get update
    apt-get install -y cuda-toolkit-12-2
    
    # Set CUDA environment variables
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> /home/ubuntu/.bashrc
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> /home/ubuntu/.bashrc
    
    # Install cuDNN (requires manual download)
    echo "Note: cuDNN needs to be installed manually from NVIDIA website"
fi

# Create application directory
echo "Setting up application directory..."
mkdir -p /opt/brew-master-ai
cd /opt/brew-master-ai

# Clone the application repository
echo "Cloning application repository..."
git clone https://github.com/your-username/brew-master-ai.git .
git checkout $APP_VERSION

# Create Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r data-extraction/requirements.txt

# Install additional system dependencies for NLP
echo "Installing NLP dependencies..."
python3 -m spacy download en_core_web_sm
python3 -m spacy download es_core_news_sm

# Download NLTK data
python3 -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
"

# Set up data directories
echo "Setting up data directories..."
mkdir -p /opt/brew-master-ai/data/{input,output,logs,temp}
mkdir -p /opt/brew-master-ai/data/input/{videos,audios,presentations,images}
mkdir -p /opt/brew-master-ai/data/output/{transcripts,embeddings,reports}

# Set up Qdrant vector database with Docker
echo "Setting up Qdrant vector database..."
cat > /opt/brew-master-ai/docker-compose.yml << 'EOF'
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped

volumes:
  qdrant_storage:
EOF

# Start Qdrant
cd /opt/brew-master-ai
docker-compose up -d qdrant

# Create systemd service for the application
echo "Creating systemd service..."
cat > /etc/systemd/system/brew-master-ai.service << EOF
[Unit]
Description=Brew Master AI Data Extraction Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/brew-master-ai
Environment=PATH=/opt/brew-master-ai/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/opt/brew-master-ai/venv/bin/python -m brew_master_ai.data_processor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create supervisor configuration for process management
echo "Setting up supervisor..."
cat > /etc/supervisor/conf.d/brew-master-ai.conf << EOF
[program:brew-master-ai]
command=/opt/brew-master-ai/venv/bin/python -m brew_master_ai.data_processor
directory=/opt/brew-master-ai
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/brew-master-ai.log
environment=PATH="/opt/brew-master-ai/venv/bin:/usr/local/bin:/usr/bin:/bin"
EOF

# Set up log rotation
echo "Setting up log rotation..."
cat > /etc/logrotate.d/brew-master-ai << EOF
/var/log/brew-master-ai.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        supervisorctl restart brew-master-ai
    endscript
}
EOF

# Create monitoring script
echo "Creating monitoring script..."
cat > /opt/brew-master-ai/monitor.sh << 'EOF'
#!/bin/bash

# Monitor script for Brew Master AI
LOG_FILE="/var/log/brew-master-ai-monitor.log"

echo "$(date): Starting monitoring check..." >> $LOG_FILE

# Check if Qdrant is running
if ! docker ps | grep -q qdrant; then
    echo "$(date): Qdrant is not running, restarting..." >> $LOG_FILE
    cd /opt/brew-master-ai && docker-compose restart qdrant
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 85 ]; then
    echo "$(date): Memory usage is high: ${MEM_USAGE}%" >> $LOG_FILE
fi

echo "$(date): Monitoring check completed" >> $LOG_FILE
EOF

chmod +x /opt/brew-master-ai/monitor.sh

# Add monitoring to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/brew-master-ai/monitor.sh") | crontab -

# Set up AWS CloudWatch agent
echo "Setting up CloudWatch agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
    "agent": {
        "metrics_collection_interval": 60,
        "run_as_user": "cwagent"
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/brew-master-ai.log",
                        "log_group_name": "/aws/ec2/${ENVIRONMENT}-data-extraction",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/user-data.log",
                        "log_group_name": "/aws/ec2/${ENVIRONMENT}-data-extraction",
                        "log_stream_name": "{instance_id}-user-data",
                        "timezone": "UTC"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "BrewMasterAI",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 60,
                "totalcpu": false
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "diskio": {
                "measurement": ["io_time"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            },
            "netstat": {
                "measurement": ["tcp_established", "tcp_time_wait"],
                "metrics_collection_interval": 60
            },
            "swap": {
                "measurement": ["swap_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
systemctl enable amazon-cloudwatch-agent
systemctl start amazon-cloudwatch-agent

# Set proper permissions
echo "Setting proper permissions..."
chown -R ubuntu:ubuntu /opt/brew-master-ai
chmod -R 755 /opt/brew-master-ai

# Enable and start services
echo "Enabling and starting services..."
systemctl daemon-reload
systemctl enable brew-master-ai
systemctl start brew-master-ai
systemctl enable supervisor
systemctl start supervisor

# Create health check endpoint
echo "Setting up health check endpoint..."
cat > /opt/brew-master-ai/health_check.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import psutil
import docker

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check Qdrant status
            try:
                client = docker.from_env()
                qdrant_container = client.containers.get('qdrant')
                qdrant_status = qdrant_container.status
            except:
                qdrant_status = 'unknown'
            
            health_data = {
                'status': 'healthy',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'qdrant_status': qdrant_status,
                'timestamp': psutil.boot_time()
            }
            
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    server.serve_forever()
EOF

# Install psutil for health check
/opt/brew-master-ai/venv/bin/pip install psutil docker

# Create systemd service for health check
cat > /etc/systemd/system/brew-master-ai-health.service << EOF
[Unit]
Description=Brew Master AI Health Check Service
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/brew-master-ai
Environment=PATH=/opt/brew-master-ai/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/opt/brew-master-ai/venv/bin/python health_check.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl enable brew-master-ai-health
systemctl start brew-master-ai-health

# Final setup
echo "Finalizing setup..."
systemctl daemon-reload

# Create setup completion marker
echo "Setup completed at $(date)" > /opt/brew-master-ai/setup_completed.txt

echo "Brew Master AI Data Extraction instance setup completed successfully!"
echo "Instance is ready for data processing tasks."
echo "Health check available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080/health" 