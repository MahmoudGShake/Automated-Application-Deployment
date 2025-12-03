resource "aws_security_group" "diginnocent" {
    name = "diginnocent-sg"
    description = "A secuirty group for the diginnocent app"
    vpc_id = aws_vpc.main.id
    
    ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [var.my_ip]
    description = "SSH access from my IP"
    }
    
    ingress {

    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access from anywhere"
    }

    egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
}
  tags = merge(
    var.project_tags,
    {
      Name = "main-SG"
    }
  ) 
}