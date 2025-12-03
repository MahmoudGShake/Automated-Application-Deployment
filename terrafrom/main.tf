# getting the ami data for the EC2
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "diginnocent" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.diginnocent.id]

  tags = merge(
    var.project_tags,
    {
      Name = "main-app-ec2"
    }
  )

  root_block_device {
    volume_size = 8
    volume_type = "gp3"
    encrypted   = true

    tags = merge(
      var.project_tags,
      {
        Name = "main-ebs-volume"
      }
    )
  }

  user_data = templatefile("${path.module}/user-data.sh", {
    github_repo_url   = var.github_repo_url
  })

  user_data_replace_on_change = false
}

resource "aws_eip" "diginnocent" {
  domain = "vpc"

  tags = merge(
    var.project_tags,
    {
      Name = "main-eip"
    }
  )
}

resource "aws_eip_association" "diginnocent" {
  instance_id   = aws_instance.diginnocent.id
  allocation_id = aws_eip.diginnocent.id
}
