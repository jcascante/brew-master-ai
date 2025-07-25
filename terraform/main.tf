terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "brew-master-ai"
      Environment = var.environment
      Purpose     = "whisper-transcription"
      ManagedBy   = "terraform"
      Owner       = var.owner
      CostCenter  = var.cost_center
      CreatedBy   = "terraform"
    }
  }
}

# Persistent resources (deploy once, keep running)
module "persistent" {
  source = "./modules/persistent"
  
  aws_region   = var.aws_region
  project_name = var.project_name
  environment  = var.environment
  owner        = var.owner
  cost_center  = var.cost_center
  key_name     = var.key_name
}

# Ephemeral resources (deploy/destroy as needed)
module "ephemeral" {
  source = "./modules/ephemeral"
  
  aws_region        = var.aws_region
  project_name      = var.project_name
  environment       = var.environment
  owner             = var.owner
  cost_center       = var.cost_center
  instance_type     = var.instance_type
  spot_price        = var.spot_price
  ami_id            = var.ami_id
  root_volume_size  = var.root_volume_size
  root_volume_type  = var.root_volume_type
  
  # References to persistent resources
  key_pair_name              = module.persistent.key_pair_name
  subnet_id                  = module.persistent.subnet_id
  s3_bucket_name            = module.persistent.s3_bucket_name
  iam_instance_profile_name = module.persistent.iam_instance_profile_name
  
  # Volume configuration
  volume_size       = var.volume_size
  volume_type       = var.volume_type
  
  depends_on = [module.persistent]
}

# Outputs
output "instance_id" {
  description = "ID of the Whisper EC2 instance"
  value       = module.ephemeral.instance_id
}

output "public_ip" {
  description = "Public IP of the Whisper instance"
  value       = module.ephemeral.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = module.ephemeral.ssh_command
}

output "private_key" {
  description = "Private key for SSH access"
  value       = module.persistent.private_key
  sensitive   = true
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for data storage"
  value       = module.persistent.s3_bucket_name
}

output "project_tags" {
  description = "Default tags applied to all resources"
  value = {
    Project     = "brew-master-ai"
    Environment = var.environment
    Purpose     = "whisper-transcription"
    ManagedBy   = "terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
} 