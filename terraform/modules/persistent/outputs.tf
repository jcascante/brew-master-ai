output "key_pair_name" {
  description = "Name of the key pair"
  value       = var.key_name
}

output "subnet_id" {
  description = "ID of the default subnet"
  value       = data.aws_subnets.default.ids[0]
}

output "availability_zone" {
  description = "Availability zone of the subnet"
  value       = data.aws_subnet.default.availability_zone
}

output "s3_bucket_name" {
  description = "Name of the S3 data bucket"
  value       = aws_s3_bucket.data.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 data bucket"
  value       = aws_s3_bucket.data.arn
}

output "iam_instance_profile_name" {
  description = "Name of the IAM instance profile for EC2 S3 access"
  value       = aws_iam_instance_profile.ec2_s3_profile.name
}

output "private_key" {
  description = "Private key for SSH access"
  value       = tls_private_key.whisper_key.private_key_pem
  sensitive   = true
}

 