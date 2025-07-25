terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  default_tags = {
    Project     = "brew-master-ai"
    Environment = var.environment
    Purpose     = "whisper-transcription"
    ManagedBy   = "terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
    CreatedBy   = "terraform"
  }
}

# Get availability zone for the provided subnet
data "aws_subnet" "selected" {
  id = var.subnet_id
}

# Create security group for Whisper instance
resource "aws_security_group" "whisper_sg" {
  name        = "${var.project_name}-whisper-sg"
  description = "Security group for Whisper transcription instance"
  vpc_id      = data.aws_subnet.selected.vpc_id

  # SSH access
  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.default_tags, {
    Name = "${var.project_name}-whisper-sg"
  })
}

# Create small EBS volume for temporary processing only
resource "aws_ebs_volume" "temp_data" {
  availability_zone = data.aws_subnet.selected.availability_zone
  size              = var.volume_size
  type              = var.volume_type
  encrypted         = true

  tags = merge(local.default_tags, {
    Name = "${var.project_name}-whisper-temp-volume"
    Purpose = "temporary-processing"
  })
}

resource "aws_spot_instance_request" "basic" {
  ami                    = var.ami_id
  spot_price            = var.spot_price
  instance_type         = var.instance_type
  key_name              = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.whisper_sg.id]
  subnet_id              = var.subnet_id
  wait_for_fulfillment  = true
  instance_interruption_behavior = "stop"
  iam_instance_profile  = var.iam_instance_profile_name
  
  user_data = base64encode(templatefile("${path.root}/setup_ec2.sh", {
    s3_bucket_name = var.s3_bucket_name
  }))

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = var.root_volume_type
    encrypted   = true
  }

  tags = merge(local.default_tags, {
    Name = "${var.project_name}-whisper-instance"
  })
}

resource "aws_volume_attachment" "temp_data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.temp_data.id
  instance_id = aws_spot_instance_request.basic.spot_instance_id
  
  depends_on = [aws_spot_instance_request.basic, aws_ebs_volume.temp_data]
} 