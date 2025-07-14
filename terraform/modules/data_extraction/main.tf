# IAM role for the data extraction instance
resource "aws_iam_role" "data_extraction" {
  name = "${var.environment}-data-extraction-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-data-extraction-role"
  })
}

# IAM instance profile
resource "aws_iam_instance_profile" "data_extraction" {
  name = "${var.environment}-data-extraction-profile"
  role = aws_iam_role.data_extraction.name
}

# IAM policy for S3 access
resource "aws_iam_role_policy" "data_extraction_s3" {
  name = "${var.environment}-data-extraction-s3-policy"
  role = aws_iam_role.data_extraction.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::brew-master-ai-data-*",
          "arn:aws:s3:::brew-master-ai-data-*/*"
        ]
      }
    ]
  })
}

# IAM policy for CloudWatch
resource "aws_iam_role_policy" "data_extraction_cloudwatch" {
  name = "${var.environment}-data-extraction-cloudwatch-policy"
  role = aws_iam_role.data_extraction.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM policy for Systems Manager
resource "aws_iam_role_policy" "data_extraction_ssm" {
  name = "${var.environment}-data-extraction-ssm-policy"
  role = aws_iam_role.data_extraction.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:UpdateInstanceInformation",
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Resource = "*"
      }
    ]
  })
}

# Data extraction EC2 instance
resource "aws_instance" "data_extraction" {
  ami                    = var.ami_id
  instance_type          = var.enable_gpu ? var.gpu_instance_type : var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_group_ids
  key_name               = var.key_name
  iam_instance_profile   = aws_iam_instance_profile.data_extraction.name

  root_block_device {
    volume_size = var.volume_size
    volume_type = var.volume_type
    encrypted   = true

    tags = merge(var.tags, {
      Name = "${var.environment}-data-extraction-root-volume"
    })
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    environment     = var.environment
    app_name        = var.app_name
    app_version     = var.app_version
    vector_db_host  = var.vector_db_host
    vector_db_port  = var.vector_db_port
    enable_gpu      = var.enable_gpu
    gpu_driver_url  = var.gpu_driver_url
    cuda_version    = var.cuda_version
  }))

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  monitoring = true

  tags = merge(var.tags, {
    Name = "${var.environment}-data-extraction-instance"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Elastic IP for the instance
resource "aws_eip" "data_extraction" {
  count    = var.assign_public_ip ? 1 : 0
  instance = aws_instance.data_extraction.id
  domain   = "vpc"

  tags = merge(var.tags, {
    Name = "${var.environment}-data-extraction-eip"
  })
}

# CloudWatch log group
resource "aws_cloudwatch_log_group" "data_extraction" {
  name              = "/aws/ec2/${var.environment}-data-extraction"
  retention_in_days = 7

  tags = merge(var.tags, {
    Name = "${var.environment}-data-extraction-logs"
  })
}

# CloudWatch alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count               = var.enable_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.environment}-data-extraction-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EC2 CPU utilization"
  alarm_actions       = var.alarm_actions

  dimensions = {
    InstanceId = aws_instance.data_extraction.id
  }
}

resource "aws_cloudwatch_metric_alarm" "memory_high" {
  count               = var.enable_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.environment}-data-extraction-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "System/Linux"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors EC2 memory utilization"
  alarm_actions       = var.alarm_actions

  dimensions = {
    InstanceId = aws_instance.data_extraction.id
  }
}

# Backup configuration
resource "aws_backup_vault" "data_extraction" {
  count = var.enable_backup ? 1 : 0
  name  = "${var.environment}-data-extraction-backup-vault"

  tags = merge(var.tags, {
    Name = "${var.environment}-data-extraction-backup-vault"
  })
}

resource "aws_backup_plan" "data_extraction" {
  count = var.enable_backup ? 1 : 0
  name  = "${var.environment}-data-extraction-backup-plan"

  rule {
    rule_name         = "daily_backup"
    target_vault_name = aws_backup_vault.data_extraction[0].name
    schedule          = "cron(0 2 * * ? *)"  # Daily at 2 AM UTC

    lifecycle {
      delete_after = var.backup_retention_days
    }
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-data-extraction-backup-plan"
  })
}

resource "aws_backup_selection" "data_extraction" {
  count        = var.enable_backup ? 1 : 0
  name         = "${var.environment}-data-extraction-backup-selection"
  plan_id      = aws_backup_plan.data_extraction[0].id
  iam_role_arn = aws_iam_role.backup[0].arn

  resources = [
    aws_instance.data_extraction.arn
  ]
}

# IAM role for backup
resource "aws_iam_role" "backup" {
  count = var.enable_backup ? 1 : 0
  name  = "${var.environment}-backup-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backup" {
  count      = var.enable_backup ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
  role       = aws_iam_role.backup[0].name
} 