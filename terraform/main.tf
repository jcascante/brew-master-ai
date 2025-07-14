terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "brew-master-ai-terraform-state"
    key            = "data-extraction/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "brew-master-ai-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "brew-master-ai"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data sources for default VPC
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security groups (simplified for default VPC)
module "security_groups" {
  source = "./modules/security_groups"
  
  environment = var.environment
  vpc_id      = data.aws_vpc.default.id
}

# Data extraction EC2 instance
module "data_extraction" {
  source = "./modules/data_extraction"
  
  environment           = var.environment
  instance_type        = var.data_extraction_instance_type
  ami_id               = data.aws_ami.ubuntu.id
  subnet_id            = data.aws_subnets.default.ids[0]  # Use first default subnet
  security_group_ids   = [module.security_groups.data_extraction_sg_id]
  key_name             = var.key_name
  volume_size          = var.data_extraction_volume_size
  volume_type          = var.data_extraction_volume_type
  
  # GPU configuration
  enable_gpu           = var.enable_gpu
  gpu_instance_type    = var.gpu_instance_type
  
  # Application configuration
  app_name             = "brew-master-ai"
  app_version          = var.app_version
  
  # Vector database configuration
  vector_db_host       = var.vector_db_host
  vector_db_port       = var.vector_db_port
  
  depends_on = [module.security_groups]
}

# S3 bucket for data storage
module "data_storage" {
  source = "./modules/data_storage"
  
  environment = var.environment
  bucket_name = "brew-master-ai-data-${var.environment}"
}

# Outputs
output "data_extraction_instance_id" {
  description = "ID of the data extraction EC2 instance"
  value       = module.data_extraction.instance_id
}

output "data_extraction_public_ip" {
  description = "Public IP of the data extraction instance"
  value       = module.data_extraction.public_ip
}

output "data_extraction_private_ip" {
  description = "Private IP of the data extraction instance"
  value       = module.data_extraction.private_ip
}

output "data_storage_bucket" {
  description = "S3 bucket for data storage"
  value       = module.data_storage.bucket_name
}

output "vpc_id" {
  description = "Default VPC ID"
  value       = data.aws_vpc.default.id
}

output "subnet_id" {
  description = "Default subnet ID used for the instance"
  value       = data.aws_subnets.default.ids[0]
} 