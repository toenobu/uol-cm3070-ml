resource "aws_s3_bucket" "cm3070_ml" {
programboy-cm3070-foobarfoobarfoobarml
}

# Block public access (recommended for security)
resource "aws_s3_bucket_public_access_block" "cm3070_ml" {
  bucket = aws_s3_bucket.cm3070_ml.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configure S3 to notify Lambda when an object is created
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.cm3070_ml.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.serverless_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "picutre"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
