# Brew Master AI - Infrastructure Summary

## 🏗️ Architecture Overview

This Terraform infrastructure creates a complete AWS environment for running the Brew Master AI data extraction system with maximum resource utilization and GPU support.

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Infrastructure                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Public Subnet │    │  Private Subnet │                │
│  │                 │    │                 │                │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │                │
│  │ │Internet GW  │ │    │ │EC2 Instance │ │                │
│  │ └─────────────┘ │    │ │             │ │                │
│  │                 │    │ │• GPU Support│ │                │
│  │ ┌─────────────┐ │    │ │• Qdrant DB │ │                │
│  │ │NAT Gateway  │ │    │ │• Python App│ │                │
│  │ └─────────────┘ │    │ │• Monitoring│ │                │
│  └─────────────────┘    │ └─────────────┘ │                │
│                         └─────────────────┘                │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    S3 Storage                           │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ │
│  │  │ Raw Data    │ │ Processed   │ │ Logs        │       │ │
│  │  │ Bucket      │ │ Data Bucket │ │ Bucket      │       │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  CloudWatch                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ │
│  │  │ Metrics     │ │ Logs        │ │ Alarms      │       │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Key Features

### 1. **GPU-Optimized EC2 Instance**
- **Instance Types**: 
  - Development: `g4dn.xlarge` (4 vCPU, 16 GB RAM, 1 GPU)
  - Production: `g5.xlarge` (4 vCPU, 16 GB RAM, 1 GPU)
- **GPU Support**: NVIDIA drivers, CUDA toolkit, cuDNN
- **Storage**: 100-200 GB GP3 volumes with encryption

### 2. **Complete Application Stack**
- **Operating System**: Ubuntu 22.04 LTS
- **Python Environment**: Virtual environment with all dependencies
- **Docker**: For containerized services
- **Qdrant Vector Database**: Running in Docker for embeddings
- **FFmpeg**: For audio/video processing
- **Tesseract**: For OCR processing
- **NLP Libraries**: spaCy, NLTK, sentence-transformers

### 3. **Security & Networking**
- **VPC**: Private subnets with NAT Gateway
- **Security Groups**: Restrictive access controls
- **IAM Roles**: Least privilege access
- **Encryption**: S3, EBS, and data in transit
- **VPC Flow Logs**: Network traffic monitoring

### 4. **Monitoring & Observability**
- **CloudWatch**: Metrics, logs, and alarms
- **Health Checks**: HTTP endpoint for monitoring
- **Log Rotation**: Automated log management
- **Backup**: AWS Backup with configurable retention

### 5. **Data Storage**
- **S3 Buckets**: 
  - Raw data storage
  - Processed data storage
  - Logs storage
- **Lifecycle Policies**: Cost optimization
- **Versioning**: Data protection
- **Encryption**: AES256 encryption

## 📁 File Structure

```
terraform/
├── main.tf                          # Main Terraform configuration
├── variables.tf                     # Variable definitions
├── deploy.sh                        # Deployment automation script
├── README.md                        # Comprehensive documentation
├── INFRASTRUCTURE_SUMMARY.md        # This file
├── environments/
│   ├── dev.tfvars                   # Development environment config
│   └── prod.tfvars                  # Production environment config
└── modules/
    ├── vpc/                         # VPC and networking
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── security_groups/             # Security group definitions
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── data_extraction/             # EC2 instance and application
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── user_data.sh             # Instance setup script
    └── data_storage/                # S3 buckets and storage
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## 🛠️ Deployment Process

### 1. **Prerequisites Setup**
```bash
# Configure AWS CLI
aws configure

# Run setup script
./deploy.sh setup dev
```

### 2. **Deploy Infrastructure**
```bash
# Deploy development environment
./deploy.sh deploy dev

# Deploy production environment
./deploy.sh deploy prod
```

### 3. **Monitor Deployment**
```bash
# Check instance status
aws ec2 describe-instances --filters "Name=tag:Name,Values=*data-extraction*"

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/ec2"
```

## 🔧 Application Setup

The EC2 instance automatically sets up:

### System Packages
- Python 3.10+, pip, venv
- Docker & Docker Compose
- FFmpeg for audio/video processing
- Tesseract OCR with Spanish language support
- NVIDIA drivers and CUDA toolkit (GPU instances)
- Monitoring tools (htop, iotop, nvtop)

### Python Environment
- Virtual environment in `/opt/brew-master-ai/venv`
- All dependencies from `requirements.txt`
- spaCy models (English and Spanish)
- NLTK data downloads

### Application Services
- **Qdrant Vector Database**: Running on port 6333
- **Health Check Service**: Running on port 8080
- **Application Service**: Managed by systemd
- **Monitoring Script**: Cron job every 5 minutes

### Data Directories
```
/opt/brew-master-ai/
├── data/
│   ├── input/
│   │   ├── videos/
│   │   ├── audios/
│   │   ├── presentations/
│   │   └── images/
│   ├── output/
│   │   ├── transcripts/
│   │   ├── embeddings/
│   │   └── reports/
│   ├── logs/
│   └── temp/
└── venv/
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint
- **URL**: `http://<instance-ip>:8080/health`
- **Response**: JSON with system metrics
```json
{
  "status": "healthy",
  "cpu_percent": 15.2,
  "memory_percent": 45.8,
  "disk_percent": 23.1,
  "qdrant_status": "running",
  "timestamp": 1640995200
}
```

### CloudWatch Metrics
- **CPU Utilization**: Average, idle, iowait
- **Memory Usage**: Used percentage
- **Disk Usage**: Used percentage and I/O
- **Network**: TCP connections
- **Custom Metrics**: Application-specific metrics

### Alarms
- **High CPU**: >80% for 2 periods
- **High Memory**: >85% for 2 periods
- **High Disk**: >80% usage

## 🔒 Security Features

### Network Security
- **Private Subnets**: Instances in private subnets
- **Security Groups**: Minimal required access
- **NAT Gateway**: Outbound internet access
- **VPC Flow Logs**: Traffic monitoring

### Data Security
- **S3 Encryption**: AES256 server-side encryption
- **EBS Encryption**: Volume encryption
- **IAM Roles**: Least privilege access
- **Key Management**: Secure key pair handling

### Access Control
- **SSH Access**: Restricted to VPC
- **Application Ports**: Configurable access
- **CloudWatch Logs**: Audit trail
- **Backup Encryption**: Encrypted backups

## 💰 Cost Optimization

### Instance Optimization
- **Right-sizing**: Appropriate instance types
- **Auto-scaling**: Production environments
- **Spot Instances**: Development (optional)
- **Reserved Instances**: Production (recommended)

### Storage Optimization
- **S3 Lifecycle**: Automatic tiering
- **GP3 Volumes**: Better price/performance
- **Data Archival**: Glacier for old data
- **Compression**: Automatic compression

### Monitoring Costs
- **CloudWatch Alarms**: Cost alerts
- **Resource Tagging**: Cost allocation
- **Usage Monitoring**: Track resource usage
- **Cleanup Scripts**: Remove unused resources

## 🚨 Troubleshooting

### Common Issues

1. **Instance Not Starting**
   ```bash
   # Check CloudWatch logs
   aws logs describe-log-streams --log-group-name "/aws/ec2/dev-data-extraction"
   
   # Check security groups
   aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
   ```

2. **Application Not Running**
   ```bash
   # SSH to instance
   ssh -i brew-master-ai-dev-key.pem ubuntu@<instance-ip>
   
   # Check services
   sudo systemctl status brew-master-ai
   sudo systemctl status brew-master-ai-health
   
   # Check Docker
   docker ps
   docker logs qdrant
   ```

3. **GPU Issues**
   ```bash
   # Check GPU status
   nvidia-smi
   
   # Check CUDA
   nvcc --version
   
   # Check drivers
   lsmod | grep nvidia
   ```

### Useful Commands

```bash
# Get instance information
aws ec2 describe-instances --filters "Name=tag:Name,Values=*data-extraction*"

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxxxxxxxx \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average

# Check S3 buckets
aws s3 ls s3://brew-master-ai-data-dev/

# Check CloudWatch logs
aws logs filter-log-events \
  --log-group-name "/aws/ec2/dev-data-extraction" \
  --start-time 1640995200000
```

## 🔄 Maintenance

### Regular Tasks
- **Security Updates**: Monthly system updates
- **Backup Verification**: Weekly backup tests
- **Cost Review**: Monthly cost analysis
- **Performance Monitoring**: Continuous monitoring

### Scaling
- **Horizontal**: Add more instances
- **Vertical**: Increase instance size
- **Auto-scaling**: Based on metrics
- **Load Balancing**: For multiple instances

### Updates
- **Application Updates**: Deploy new versions
- **Infrastructure Updates**: Terraform apply
- **Security Patches**: Automated updates
- **Dependency Updates**: Regular updates

## 📈 Performance Optimization

### GPU Utilization
- **CUDA Optimization**: Proper CUDA version
- **Memory Management**: GPU memory monitoring
- **Batch Processing**: Optimize batch sizes
- **Model Selection**: Choose appropriate models

### CPU Optimization
- **Parallel Processing**: Multi-threading
- **Process Management**: Supervisor configuration
- **Resource Limits**: Proper resource allocation
- **Caching**: Implement caching strategies

### Storage Optimization
- **I/O Optimization**: Use GP3 volumes
- **Data Compression**: Compress large files
- **Caching**: Local caching for frequently accessed data
- **Cleanup**: Regular cleanup of temporary files

## 🎯 Next Steps

1. **Deploy Infrastructure**: Use the deployment script
2. **Configure Application**: Update application settings
3. **Test Functionality**: Run data extraction tests
4. **Monitor Performance**: Set up monitoring dashboards
5. **Scale as Needed**: Add more instances or resources
6. **Optimize Costs**: Review and optimize resource usage

## 📞 Support

For issues and questions:
1. Check CloudWatch logs and metrics
2. Review Terraform documentation
3. Check application logs on the instance
4. Contact the development team

---

**Note**: This infrastructure is designed for maximum resource utilization and GPU support. Adjust instance types and configurations based on your specific workload requirements and budget constraints. 