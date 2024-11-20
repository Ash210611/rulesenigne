# data "template_file" "key_policy" {
#   template = templatefile("${path.module}/kms_key_policy.tftpl",
#     {
#       account_id             = data.aws_caller_identity.current.account_id
#       kms_key_administrators = jsonencode([for role in var.kms_key_administrators : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${role}"])
#       kms_key_users          = jsonencode([for role in var.kms_key_users : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${role}"])
#   })
# }

resource "aws_kms_key_policy" "ecr_key_policy" {
  key_id = aws_kms_key.ecr_key.key_id
  policy = data.aws_iam_policy_document.kms_key_policy.json
}

resource "aws_kms_key" "ecr_key" {
  deletion_window_in_days  = 7
  description              = "CMK for ${var.project_name} ECR images"
  enable_key_rotation      = true
  is_enabled               = true
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
#   policy                   = aws_kms_key_policy.ecr_key_policy.policy

  tags = var.required_common_tags
}

resource "aws_kms_alias" "key_alias" {
  name          = "alias/${var.project_name}-ecr-key"
  target_key_id = aws_kms_key.ecr_key.key_id
}