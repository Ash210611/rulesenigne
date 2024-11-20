data "aws_iam_policy_document" "kms_access" {
  statement {
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    effect = "Allow"
    resources = [
      aws_kms_key.ecr_key.arn,
    ]
  }
}

# data "aws_iam_policy_document" "kms_key_policy" {
#   statement {
#     sid = "Enable IAM User Permissions"
#     actions = [
#       "kms:*"
#     ]
#     effect = "Allow"
#     principals {
#       type = "AWS"
#       identifiers = [
#         "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
#       ]
#     }
#     resources = ["*",
#     ]
#   }

data "aws_iam_policy_document" "kms_key_policy" {
  statement {
    sid = "Allow access for Key Administrators"
    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion"
    ]
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = ["*"]
    }
    resources = ["*"]
  }

#   statement {
#     sid = "Allow KMS Key Management"
#     actions = [
#       "kms:*"
#     ]
#     effect = "Allow"
#     principals {
#       type        = "AWS"
#       identifiers = ["*"]
#     }
#
#     resources = [aws_kms_key.alarm_topic_key.arn]
#     condition {
#       test     = "ArnLike"
#       variable = "AWS:PrincipalArn"
#       values = [
#         data.aws_iam_role.deployer.arn,
#         "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_Admin_*",
#       ]
#     }
#   }
}
