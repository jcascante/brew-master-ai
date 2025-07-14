# Brew Master AI - AWS Infrastructure (Simplified)

This directory contains the Terraform configuration for deploying the Brew Master AI data extraction infrastructure on AWS using the **default VPC** for simplified development.

## Architecture Overview

The infrastructure consists of:

- **Default VPC**: Using AWS default VPC for simplicity
- **EC2 Instance**: Optimized for data extraction with GPU support
- **S3 Buckets**: For data storage, processed data, and logs
- **Security Groups**: Restrictive access controls
- **CloudWatch**: Monitoring and logging
- **AWS Backup**: Automated backups
- **Qdrant Vector Database**: Running in Docker for embeddings storage

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **AWS S3 Bucket** for Terraform state (create manually first)
4. **DynamoDB Table** for state locking (create manually first)
5. **EC2 Key Pair** for SSH access
6. **Default VPC** in your AWS account (usually exists by default)

## Quick Start

### 1. Create S3 Backend Infrastructure

First, create the S3 bucket and DynamoDB table for Terraform state:

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://brew-master-ai-terraform-state

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket brew-master-ai-terraform-state \
    --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
    --table-name brew-master-ai-terraform-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

### 2. Create EC2 Key Pair

```bash
# Create key pair for SSH access
aws ec2 create-key-pair \
    --key-name brew-master-ai-dev-key \
    --query 'KeyMaterial' \
    --output text > brew-master-ai-dev-key.pem

chmod 400 brew-master-ai-dev-key.pem
```

### 3. Deploy Infrastructure

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Plan deployment for development
terraform plan -var-file="environments/dev.tfvars"

# Apply deployment
terraform apply -var-file="environments/dev.tfvars"
```

## Configuration

### Environment Variables

The infrastructure supports multiple environments through `.tfvars` files:

- `environments/dev.tfvars` - Development environment (simplified)
- `environments/prod.tfvars` - Production environment (simplified)

### Key Configuration Options

#### Instance Types

- **CPU-only**: `t3.xlarge` (4 vCPU, 16 GB RAM) - Good for development
- **GPU-enabled**: `g4dn.xlarge` (4 vCPU, 16 GB RAM, 1 GPU) - For production workloads

#### Storage

- **Root Volume**: 100-200 GB GP3 (configurable)
- **S3 Buckets**: 
  - Main data storage
  - Processed data storage
  - Logs storage

#### Networking

- **Default VPC**: Uses AWS default VPC
- **Public Subnets**: Instances in public subnets with direct internet access
- **Security Groups**: Restrictive access controls

## Modules

### Security Groups Module (`modules/security_groups/`)

Defines security rules:
- Data extraction instance access
- Load balancer access (optional)
- Redis access (optional)
- RDS access (optional)

### Data Extraction Module (`modules/data_extraction/`)

Creates the main EC2 instance:
- Ubuntu 22.04 LTS
- GPU support (optional)
- IAM roles and policies
- CloudWatch monitoring
- AWS Backup configuration
- User data script for application setup

### Data Storage Module (`modules/data_storage/`)

Creates S3 buckets:
- Main data storage
- Processed data storage
- Logs storage
- Lifecycle policies
- Encryption
- CloudFront distribution (optional)

## Application Setup

The EC2 instance automatically sets up:

1. **System Packages**: Python, Docker, FFmpeg, Tesseract, etc.
2. **GPU Drivers**: NVIDIA drivers and CUDA toolkit (if enabled)
3. **Python Environment**: Virtual environment with all dependencies
4. **Qdrant Database**: Running in Docker
5. **Application Code**: Cloned from repository
6. **Monitoring**: CloudWatch agent and health checks
7. **Services**: Systemd services for application and health checks

## Monitoring and Logging

### CloudWatch

- **Metrics**: CPU, memory, disk usage
- **Logs**: Application logs, user data logs
- **Alarms**: High CPU/memory usage alerts

### Health Checks

- **Endpoint**: `http://instance-ip:8080/health`
- **Checks**: System metrics, Qdrant status
- **Response**: JSON with health status

## Security

### Network Security

- Default VPC with public subnets
- Security groups with minimal required access
- Direct internet access (no NAT Gateway needed)

### Data Security

- S3 bucket encryption (AES256)
- EBS volume encryption
- IAM roles with least privilege
- HTTPS-only access

### Access Control

- SSH access via security groups
- Application ports configurable
- CloudWatch logs for audit trail

## Cost Optimization

### Instance Types

- Use spot instances for development (not configured by default)
- Right-size instances based on workload
- Enable auto-scaling for production

### Storage

- S3 lifecycle policies for cost optimization
- GP3 volumes for better price/performance
- CloudFront for data distribution (optional)

### Monitoring

- CloudWatch alarms for cost alerts
- Resource tagging for cost allocation

## Troubleshooting

### Common Issues

1. **Instance Not Starting**
   - Check CloudWatch logs
   - Verify security group rules
   - Check IAM role permissions

2. **Application Not Running**
   - SSH to instance and check services
   - Review application logs
   - Check Docker containers

3. **GPU Not Working**
   - Verify instance type has GPU
   - Check NVIDIA drivers installation
   - Verify CUDA installation

### Useful Commands

```bash
# SSH to instance
ssh -i brew-master-ai-dev-key.pem ubuntu@<instance-ip>

# Check application status
sudo systemctl status brew-master-ai

# Check Docker containers
docker ps

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/ec2/dev-data-extraction"

# Check health endpoint
curl http://<instance-ip>:8080/health
```

## Cleanup

To destroy the infrastructure:

```bash
# Destroy infrastructure
terraform destroy -var-file="environments/dev.tfvars"

# Clean up S3 backend (optional)
aws s3 rb s3://brew-master-ai-terraform-state --force
aws dynamodb delete-table --table-name brew-master-ai-terraform-locks
```

## Contributing

1. Create feature branch
2. Update configuration files
3. Test with `terraform plan`
4. Submit pull request

## Support

For issues and questions:
1. Check CloudWatch logs
2. Review Terraform documentation
3. Contact the development team

## Migration to Custom VPC

When you're ready to move to production with a custom VPC:

1. Uncomment the VPC module in `main.tf`
2. Add VPC-related variables back to `variables.tf`
3. Update environment configurations
4. Run `terraform plan` to see the changes
5. Apply the changes with `terraform apply`

This simplified setup is perfect for development and can be easily upgraded to a production-grade VPC when needed. 