terraform {
  required_version = ">= 0.14.10"

  required_providers {
    aws = {
      version = "~> 4.35"
      source  = "hashicorp/aws"
    }
    null = {
      version = "~> 2.1.2"
      source  = "hashicorp/null"
    }
    random = {
      version = "~> 2.3.0"
      source  = "hashicorp/random"
    }
  }
}