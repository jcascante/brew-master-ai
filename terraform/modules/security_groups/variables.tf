variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_cidr_blocks" {
  description = "List of VPC CIDR blocks for internal access"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "allowed_ssh_cidrs" {
  description = "List of CIDR blocks allowed to SSH to instances"
  type        = list(string)
  default     = ["10.0.0.0/16"]  # Restrict to VPC by default
}

variable "allowed_http_cidrs" {
  description = "List of CIDR blocks allowed to access HTTP/HTTPS"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Allow from anywhere by default
}

variable "enable_load_balancer" {
  description = "Enable load balancer security group"
  type        = bool
  default     = false
}

variable "enable_redis" {
  description = "Enable Redis security group"
  type        = bool
  default     = false
}

variable "enable_rds" {
  description = "Enable RDS security group"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
} 