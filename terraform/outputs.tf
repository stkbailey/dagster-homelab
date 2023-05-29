output "dagster_cloud_access_key_id" {
  value = aws_iam_access_key.dagster_cloud.id
  sensitive = true
}

output "dagster_cloud_secret_access_key" {
  value = aws_iam_access_key.dagster_cloud.secret
  sensitive = true
}