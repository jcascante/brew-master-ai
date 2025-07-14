output "data_extraction_sg_id" {
  description = "ID of the data extraction security group"
  value       = aws_security_group.data_extraction.id
}

output "data_extraction_sg_name" {
  description = "Name of the data extraction security group"
  value       = aws_security_group.data_extraction.name
}

output "load_balancer_sg_id" {
  description = "ID of the load balancer security group"
  value       = var.enable_load_balancer ? aws_security_group.load_balancer[0].id : null
}

output "redis_sg_id" {
  description = "ID of the Redis security group"
  value       = var.enable_redis ? aws_security_group.redis[0].id : null
}

output "rds_sg_id" {
  description = "ID of the RDS security group"
  value       = var.enable_rds ? aws_security_group.rds[0].id : null
} 