# Development Environment Configuration (Simplified - No Custom VPC)
environment = "dev"
aws_region  = "us-east-1"

# Instance Configuration
data_extraction_instance_type = "t3.xlarge"  # 4 vCPU, 16 GB RAM
gpu_instance_type            = "g4dn.xlarge" # 4 vCPU, 16 GB RAM, 1 GPU
enable_gpu                   = true
data_extraction_volume_size  = 100
data_extraction_volume_type  = "gp3"

# Application Configuration
app_version = "main"

# Vector Database Configuration
vector_db_host = "localhost"
vector_db_port = 6333

# Security Configuration
key_name = "brew-master-ai-dev-key"

# Scaling Configuration
enable_auto_scaling = false
min_size           = 1
max_size           = 2
desired_capacity   = 1

# Monitoring Configuration
enable_cloudwatch       = true
enable_cloudwatch_alarms = true

# Backup Configuration
enable_backup           = true
backup_retention_days   = 7

# Additional Tags
tags = {
  Environment = "development"
  Owner       = "BrewMasterAI"
  Purpose     = "DataExtraction"
  CostCenter  = "AI-Research"
  Project     = "BrewMasterAI"
  Note        = "Using default VPC for development"
} 