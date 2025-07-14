output "bucket_name" {
  description = "Name of the main data storage bucket"
  value       = aws_s3_bucket.data.bucket
}

output "bucket_arn" {
  description = "ARN of the main data storage bucket"
  value       = aws_s3_bucket.data.arn
}

output "bucket_domain_name" {
  description = "Domain name of the main data storage bucket"
  value       = aws_s3_bucket.data.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "Regional domain name of the main data storage bucket"
  value       = aws_s3_bucket.data.bucket_regional_domain_name
}

output "processed_bucket_name" {
  description = "Name of the processed data storage bucket"
  value       = aws_s3_bucket.processed.bucket
}

output "processed_bucket_arn" {
  description = "ARN of the processed data storage bucket"
  value       = aws_s3_bucket.processed.arn
}

output "logs_bucket_name" {
  description = "Name of the logs storage bucket"
  value       = aws_s3_bucket.logs.bucket
}

output "logs_bucket_arn" {
  description = "ARN of the logs storage bucket"
  value       = aws_s3_bucket.logs.arn
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.data[0].id : null
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.data[0].domain_name : null
} 