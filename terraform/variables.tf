variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "key_name" {
  description = "Name of the EC2 key pair to use for SSH access"
  type        = string
  default     = "brew-master-ai-key"
}

# Data Extraction Instance Configuration
variable "data_extraction_instance_type" {
  description = "EC2 instance type for data extraction (CPU-only)"
  type        = string
  default     = "t3.xlarge"  # 4 vCPU, 16 GB RAM
  
  validation {
    condition     = can(regex("^[a-z0-9]+\\.[a-z0-9]+$", var.data_extraction_instance_type))
    error_message = "Instance type must be in format: type.size (e.g., t3.xlarge)."
  }
}

variable "gpu_instance_type" {
  description = "EC2 instance type for GPU-enabled data extraction"
  type        = string
  default     = "g4dn.xlarge"  # 4 vCPU, 16 GB RAM, 1 GPU
  
  validation {
    condition     = can(regex("^[a-z0-9]+\\.[a-z0-9]+$", var.gpu_instance_type))
    error_message = "GPU instance type must be in format: type.size (e.g., g4dn.xlarge)."
  }
}

variable "enable_gpu" {
  description = "Enable GPU support for data extraction"
  type        = bool
  default     = true
}

variable "data_extraction_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 100
  
  validation {
    condition     = var.data_extraction_volume_size >= 20
    error_message = "Volume size must be at least 20 GB."
  }
}

variable "data_extraction_volume_type" {
  description = "Type of the root volume"
  type        = string
  default     = "gp3"
  
  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.data_extraction_volume_type)
    error_message = "Volume type must be one of: gp2, gp3, io1, io2."
  }
}

# Application Configuration
variable "app_version" {
  description = "Version of the Brew Master AI application to deploy"
  type        = string
  default     = "latest"
}

variable "vector_db_host" {
  description = "Host for the vector database"
  type        = string
  default     = "localhost"
}

variable "vector_db_port" {
  description = "Port for the vector database"
  type        = number
  default     = 6333
  
  validation {
    condition     = var.vector_db_port >= 1 && var.vector_db_port <= 65535
    error_message = "Port must be between 1 and 65535."
  }
}

# Resource Tags
variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default = {
    Owner       = "BrewMasterAI"
    Purpose     = "DataExtraction"
    CostCenter  = "AI-Research"
  }
}

# Scaling Configuration
variable "enable_auto_scaling" {
  description = "Enable auto scaling for the data extraction instance"
  type        = bool
  default     = false
}

variable "min_size" {
  description = "Minimum number of instances in auto scaling group"
  type        = number
  default     = 1
  
  validation {
    condition     = var.min_size >= 0
    error_message = "Minimum size must be 0 or greater."
  }
}

variable "max_size" {
  description = "Maximum number of instances in auto scaling group"
  type        = number
  default     = 3
  
  validation {
    condition     = var.max_size >= var.min_size
    error_message = "Maximum size must be greater than or equal to minimum size."
  }
}

variable "desired_capacity" {
  description = "Desired number of instances in auto scaling group"
  type        = number
  default     = 1
  
  validation {
    condition     = var.desired_capacity >= var.min_size && var.desired_capacity <= var.max_size
    error_message = "Desired capacity must be between minimum and maximum size."
  }
}

# Monitoring Configuration
variable "enable_cloudwatch" {
  description = "Enable CloudWatch monitoring and logging"
  type        = bool
  default     = true
}

variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms for monitoring"
  type        = bool
  default     = true
}

# Backup Configuration
variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention days must be between 1 and 365."
  }
} 