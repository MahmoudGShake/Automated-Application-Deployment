data "aws_availability_zones" "available" {
    state = "available"
}

resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    enable_dns_support = true
    enable_dns_hostnames = true
    tags = merge(
    var.project_tags,
    {
      Name = "main-vpc"
    }
  )        
}

resource "aws_internet_gateway" "main-igw" {
    vpc_id = aws_vpc.main.id
    tags = merge(
    var.project_tags,
    {
      Name = "main-IGW"
    }
  )        
}

resource "aws_subnet" "public" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.0.1.0/24"
    map_public_ip_on_launch = true
    availability_zone = data.aws_availability_zones.available.names[0]

    tags = merge(
    var.project_tags,
    {
      Name = "main-subnet"
    }
  )  
}

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.main-igw.id
    }
    tags = merge(
    var.project_tags,
    {
      Name = "main-route-table"
    }
  )        
}

resource "aws_route_table_association" "public" {
    subnet_id = aws_subnet.public.id
    route_table_id = aws_route_table.public.id
}
