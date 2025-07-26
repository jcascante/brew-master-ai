variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "brew-master-ai"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "data-team"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "ai-processing"
}

variable "instance_type" {
  description = "EC2 instance type for Whisper transcription"
  type        = string
  default     = "c5.2xlarge"  # Good balance for CPU-based Whisper processing
}

variable "spot_price" {
  description = "Maximum bid price for Spot instance (leave empty for on-demand price)"
  type        = string
  default     = ""
}

variable "key_name" {
  description = "Name of the EC2 key pair to use for SSH access"
  type        = string
  default     = "brew-master-ai-key"
}

variable "volume_size" {
  description = "Size of the EBS data volume in GB (for temporary processing only)"
  type        = number
  default     = 20  # Minimal size for temp processing - data stored in S3
}

variable "volume_type" {
  description = "Type of the EBS data volume"
  type        = string
  default     = "gp3"
  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.volume_type)
    error_message = "Volume type must be one of: gp2, gp3, io1, io2."
  }
}

variable "root_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 20
}

variable "root_volume_type" {
  description = "Type of the root volume"
  type        = string
  default     = "gp3"
  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.root_volume_type)
    error_message = "Root volume type must be one of: gp2, gp3, io1, io2."
  }
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
  default     = "ami-0150ccaf51ab55a51"  # Amazon Linux 2023 AMI 2023.8.20250707.0 x86_64 HVM kernel-6.1
}

variable "s3_bucket" {
  description = "S3 bucket name for storing audio files and transcripts"
  type        = string
  default     = "brew-master-ai-data"
}