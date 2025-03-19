terraform {
  required_providers {
    aws = {
      version = "~> 5.9"
      source  = "hashicorp/aws"
    }

    sops = {
      source  = "carlpett/sops"
      version = "1.1.1"
    }
  }
  required_version = ">= 1.10.5"
}
