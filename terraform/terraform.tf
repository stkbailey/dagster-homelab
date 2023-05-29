terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.0.1"
    }
  }
  backend "s3" {
    bucket = "stkbailey-homelab-terraform"
    key    = "dagster-homelab.tfstate"
    region = "us-east-2"
  }
}

provider "aws" {
  region                   = var.region

  default_tags {
    tags = {
      name        = "stkbailey-home"
      iac_repo = "github.com/stkbailey/dagster-homelab"
    }
  }
}
