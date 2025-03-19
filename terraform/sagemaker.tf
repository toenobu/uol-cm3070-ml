resource "aws_sagemaker_notebook_instance" "notebook" {
  name                = "my-notebook-instance"
  role_arn            = aws_iam_role.sagemaker_role.arn
  instance_type       = "ml.g4dn.xlarge" # Choose appropriate instance type
  platform_identifier = "notebook-al2-v3"
  volume_size         = 6 # Size in GB

  default_code_repository = aws_sagemaker_code_repository.cm3070_ml.code_repository_name

  tags = {
    Name        = "sagemaker-notebook"
    Environment = "development"
  }
}

resource "aws_sagemaker_code_repository" "cm3070_ml" {
  code_repository_name = "cm3070-ml"

  git_config {
    repository_url = "https://github.com/toenobu/uol-cm3070-ml.git"
    secret_arn     = aws_secretsmanager_secret.cm3070_ml.arn
  }

  depends_on = [aws_secretsmanager_secret_version.cm3070_ml]
}
