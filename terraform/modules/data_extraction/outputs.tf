output "instance_id" {
  description = "ID of the data extraction EC2 instance"
  value       = aws_instance.data_extraction.id
}

output "instance_arn" {
  description = "ARN of the data extraction EC2 instance"
  value       = aws_instance.data_extraction.arn
}

output "public_ip" {
  description = "Public IP of the data extraction instance"
  value       = var.assign_public_ip ? aws_eip.data_extraction[0].public_ip : aws_instance.data_extraction.public_ip
}

output "private_ip" {
  description = "Private IP of the data extraction instance"
  value       = aws_instance.data_extraction.private_ip
}

output "instance_type" {
  description = "Instance type of the data extraction instance"
  value       = aws_instance.data_extraction.instance_type
}

output "availability_zone" {
  description = "Availability zone of the data extraction instance"
  value       = aws_instance.data_extraction.availability_zone
}

output "iam_role_arn" {
  description = "ARN of the IAM role for the data extraction instance"
  value       = aws_iam_role.data_extraction.arn
}

output "iam_role_name" {
  description = "Name of the IAM role for the data extraction instance"
  value       = aws_iam_role.data_extraction.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for the data extraction instance"
  value       = aws_cloudwatch_log_group.data_extraction.name
}

output "backup_vault_arn" {
  description = "ARN of the backup vault"
  value       = var.enable_backup ? aws_backup_vault.data_extraction[0].arn : null
}

output "backup_plan_arn" {
  description = "ARN of the backup plan"
  value       = var.enable_backup ? aws_backup_plan.data_extraction[0].arn : null
} 