/*
    Variable declarations. These default values should not be modified
    To set these vars, update the vpc.auto.tfvars file
*/

variable "required_common_tags" {
  default = {
    # Required Tags
    CostCenter = ""
    AssetOwner = ""
    CiId       = ""
    AsaqId     = ""
  }
}

variable "name_prefix" {
  description = "Optional prefix for VPC name and related objects - recommended to use a meaningful project name prefix here."
  type        = string
  default     = "dataops-rules-engine"
}

variable "extra_tags" {
  description = "Map of additional tags to tag resources with"
  type        = map(string)
  default     = {}
}

variable "eks_config" {
  description = "Optional map of settings for EKS.  Adds cluster tags and optionally creates additinoal 100.126.x subnets."
  type        = map(string)
  default     = {}
}

variable "profile" {
  description = "The AWS profile to use"
  type        = string
  default     = "saml"
}

# variable "ecr_force_delete" {
#   description = "Force delete ECR repo even if images are present. Good for development environments"
#   type        = bool
#   default     = false
# }

variable "project_name" {
  description = "The project name using these resources."
  type        = string
}

variable "kms_key_administrators" {
  description = "The IAM role names to be granted key administration privileges"
  type        = list(string)
}

variable "kms_key_users" {
  description = "The IAM role names to be granted key usage privileges"
  type        = list(string)
}