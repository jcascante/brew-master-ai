variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for Whisper transcription"
  type        = string
}

variable "spot_price" {
  description = "Maximum bid price for Spot instance (leave empty for on-demand price)"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
}

variable "root_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
}

variable "root_volume_type" {
  description = "Type of the root volume"
  type        = string
}

variable "volume_size" {
  description = "Size of the EBS data volume in GB"
  type        = number
}

variable "volume_type" {
  description = "Type of the EBS data volume"
  type        = string
}

# References to persistent resources
variable "key_pair_name" {
  description = "Name of the key pair from persistent module"
  type        = string
}

variable "subnet_id" {
  description = "ID of the subnet from persistent module"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket from persistent module"
  type        = string
}

variable "iam_instance_profile_name" {
  description = "Name of the IAM instance profile from persistent module"
  type        = string
} 