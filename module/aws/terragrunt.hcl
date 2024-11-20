generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
provider "aws" {
  region = "us-east-1"
  # TODO Update tags to reflect your team details
  default_tags {
    tags = {
      AppName     = "silverton-dataops-rules-engine"
      AssetName   = "Datops Rules Engine Repo"
      AssetOwner  = "Zachary.Hinds@CignaHealthcare.com"
      BackupOwner = "team.backup@email.com"
      TeamName    = "Brute Squad"
      SourceRepo  = "https://github.com/zilvertonz/silverton-dataops-rules-engine"
    }
  }
}
EOF
}

remote_state {
  backend = "s3"
  config = {
    disable_bucket_update = true
    bucket                = "silverton-tf-state-${get_env("TF_VAR_account_number")}-${get_env("TF_VAR_region")}"
    key                   = "${get_env("TF_VAR_repo_name")}/${path_relative_to_include()}/terraform.state"
    region                = "${get_env("TF_VAR_region", "us-east-1")}"
    dynamodb_table        = "silverton-tf-lock-${get_env("TF_VAR_account_number")}-${get_env("TF_VAR_region")}"
  }
}
