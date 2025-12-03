output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.diginnocent.id
}

output "instance_public_ip" {
  description = "Public IP address of the instance"
  value       = aws_eip.diginnocent.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the instance"
  value       = aws_instance.diginnocent.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_eip.diginnocent.public_ip}"
}

output "application_url" {
  description = "Application URL"
  value       = "http://${aws_eip.diginnocent.public_ip}"
}
