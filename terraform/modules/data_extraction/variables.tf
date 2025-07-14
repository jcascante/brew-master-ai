variable "environment" {
  description = "Environment name"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for data extraction (CPU-only)"
  type        = string
  default     = "t3.xlarge"
}

variable "gpu_instance_type" {
  description = "EC2 instance type for GPU-enabled data extraction"
  type        = string
  default     = "g4dn.xlarge"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID where the instance will be launched"
  type        = string
}

variable "security_group_ids" {
  description = "List of security group IDs"
  type        = list(string)
}

variable "key_name" {
  description = "Name of the EC2 key pair"
  type        = string
}

variable "volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 100
}

variable "volume_type" {
  description = "Type of the root volume"
  type        = string
  default     = "gp3"
}

variable "enable_gpu" {
  description = "Enable GPU support"
  type        = bool
  default     = true
}

variable "gpu_driver_url" {
  description = "URL for GPU driver download"
  type        = string
  default     = "https://us.download.nvidia.com/tesla/535.86.10/NVIDIA-Linux-x86_64-535.86.10.run"
}

variable "cuda_version" {
  description = "CUDA version to install"
  type        = string
  default     = "12.2"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "brew-master-ai"
}

variable "app_version" {
  description = "Application version to deploy"
  type        = string
  default     = "main"
}

variable "vector_db_host" {
  description = "Vector database host"
  type        = string
  default     = "localhost"
}

variable "vector_db_port" {
  description = "Vector database port"
  type        = number
  default     = 6333
}

variable "assign_public_ip" {
  description = "Assign public IP to the instance"
  type        = bool
  default     = false
}

variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "alarm_actions" {
  description = "List of ARNs for CloudWatch alarm actions"
  type        = list(string)
  default     = []
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
} 