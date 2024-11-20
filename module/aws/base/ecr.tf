resource "aws_ecr_repository" "dataops-rules-engine" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"
  # force_delete         = var.ecr_force_delete

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr_key.arn
  }

  tags = var.required_common_tags
}