resource "aws_kms_key" "cm3070_ml" {
  description         = "KMS key for db"
  key_usage           = "ENCRYPT_DECRYPT"
  is_enabled          = true
  enable_key_rotation = true
  multi_region        = false
}

output "cm3070_ml_kms_key_arn" {
  value = aws_kms_key.cm3070_ml.arn
}
