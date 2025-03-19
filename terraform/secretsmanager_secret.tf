resource "aws_secretsmanager_secret" "cm3070_ml" {
  name = "cm3070-ml"
}

resource "aws_secretsmanager_secret_version" "cm3070_ml" {
  secret_id = aws_secretsmanager_secret.cm3070_ml.id
  secret_string = jsonencode({
    username = data.sops_file.secrets.data["username"]
    password = data.sops_file.secrets.data["personal_access_token"] # Use a Personal Access Token instead of password
  })
}

data "sops_file" "secrets" {
  source_file = "secret.yaml"
}
