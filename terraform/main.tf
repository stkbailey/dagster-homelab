resource "aws_s3_bucket" "main" {
  bucket = var.bucket_name
}


resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
    }
  }
}


resource "aws_iam_access_key" "dagster_cloud" {
  user    = aws_iam_user.dagster_cloud.name
}

resource "aws_iam_user" "dagster_cloud" {
  name = "dagster_cloud"
  path = "/system/"
}

data "aws_iam_policy_document" "dagster_cloud" {
  statement {
    effect    = "Allow"
    actions   = ["s3:*"]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "dagster_cloud" {
  name   = "dagster_cloud"
  user   = aws_iam_user.dagster_cloud.name
  policy = data.aws_iam_policy_document.dagster_cloud.json
}
