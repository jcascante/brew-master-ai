# Production Environment Configuration
environment = "prod"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"

# Instance Configuration
data_extraction_instance_type = "c5.2xlarge"  # 8 vCPU, 16 GB RAM
gpu_instance_type            = "g5.xlarge"    # 4 vCPU, 16 GB RAM, 1 GPU
enable_gpu                   = true
data_extraction_volume_size  = 200
data_extraction_volume_type  = "gp3"

# Application Configuration
app_version = "v1.0.0"

# Vector Database Configuration
vector_db_host = "localhost"
vector_db_port = 6333

# Security Configuration
key_name = "brew-master-ai-prod-key"

# Scaling Configuration
enable_auto_scaling = true
min_size           = 1
max_size           = 3
desired_capacity   = 2

# Monitoring Configuration
enable_cloudwatch       = true
enable_cloudwatch_alarms = true

# Backup Configuration
enable_backup           = true
backup_retention_days   = 30

# Additional Tags
tags = {
  Environment = "production"
  Owner       = "BrewMasterAI"
  Purpose     = "DataExtraction"
  CostCenter  = "AI-Research"
  Project     = "BrewMasterAI"
  Criticality = "High"
} 