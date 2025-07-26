output "instance_id" {
  description = "ID of the Whisper EC2 instance"
  value       = aws_spot_instance_request.basic.spot_instance_id
}

output "public_ip" {
  description = "Public IP of the Whisper instance"
  value       = aws_spot_instance_request.basic.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${var.key_pair_name}.pem ec2-user@${aws_spot_instance_request.basic.public_ip}"
}

 