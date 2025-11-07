terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
}

data "aws_caller_identity" "current" {}

resource "aws_ecr_repository" "asistente_gastos" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "asistente-gastos-ecr"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
