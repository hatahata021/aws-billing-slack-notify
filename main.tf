terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
  profile = "user3"
  
  default_tags {
    tags = {
      managed_by   = "terraform"
      in_use       = "true"
    }
  }
}