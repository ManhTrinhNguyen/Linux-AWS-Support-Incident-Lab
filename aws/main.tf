terraform {
  required_version = ">= 1.6.0, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "support-incident-lab" }
  }
}
variable "region" {
  type    = string
  default = "us-west-2"
}
variable "admin_cidr" {
  description = "Your current public IPv4 address followed by /32."
  type        = string
  validation {
    condition     = can(cidrhost(var.admin_cidr, 0)) && can(regex("^[0-9.]+/32$", var.admin_cidr))
    error_message = "Use your own public IPv4 address with /32."
  }
}
variable "key_name" {
  description = "An existing EC2 key pair name in the selected region."
  type        = string
}
data "aws_ssm_parameter" "ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}
resource "aws_vpc" "lab" {
  cidr_block           = "10.77.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}
resource "aws_internet_gateway" "lab" {
  vpc_id = aws_vpc.lab.id
}
resource "aws_subnet" "lab" {
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = "10.77.1.0/24"
  map_public_ip_on_launch = true
}
resource "aws_route_table" "lab" {
  vpc_id = aws_vpc.lab.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lab.id
  }
}
resource "aws_route_table_association" "lab" {
  subnet_id      = aws_subnet.lab.id
  route_table_id = aws_route_table.lab.id
}
resource "aws_security_group" "lab" {
  name_prefix = "support-lab-"
  description = "SSH only from your workstation; HTTP uses an SSH tunnel"
  vpc_id      = aws_vpc.lab.id
  ingress {
    description = "Workstation SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_s3_bucket" "lab" {
  bucket_prefix = "support-lab-"
}
resource "aws_s3_bucket_public_access_block" "lab" {
  bucket                  = aws_s3_bucket.lab.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_object" "allowed" {
  bucket  = aws_s3_bucket.lab.id
  key     = "allowed/example.txt"
  content = "Allowed lab object"
}
resource "aws_s3_object" "restricted" {
  bucket  = aws_s3_bucket.lab.id
  key     = "restricted/example.txt"
  content = "Restricted lab object"
}
resource "aws_iam_role" "lab" {
  name_prefix = "support-lab-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy" "lab" {
  role = aws_iam_role.lab.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow", Action = ["s3:GetObject"], Resource = "${aws_s3_bucket.lab.arn}/allowed/*"
    }]
  })
}
resource "aws_iam_instance_profile" "lab" {
  name_prefix = "support-lab-"
  role        = aws_iam_role.lab.name
}
resource "aws_instance" "lab" {
  ami                    = data.aws_ssm_parameter.ami.value
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.lab.id
  vpc_security_group_ids = [aws_security_group.lab.id]
  key_name               = var.key_name
  iam_instance_profile   = aws_iam_instance_profile.lab.name
  user_data              = file("${path.module}/user-data.sh")
  metadata_options {
    http_tokens = "required"
  }
  root_block_device {
    encrypted             = true
    volume_size           = 8
    delete_on_termination = true
  }
  depends_on = [aws_route_table_association.lab]
}
output "public_ip" { value = aws_instance.lab.public_ip }
output "security_group_id" { value = aws_security_group.lab.id }
output "bucket_name" { value = aws_s3_bucket.lab.id }
