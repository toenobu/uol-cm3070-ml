# IAM role for Lambda execution
resource "aws_iam_role" "serverless_lambda" {
  name = "my-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

}

# Attach the custom S3 access policy to the serverless lambda
resource "aws_iam_role_policy_attachment" "serverless_lambda_s3_policy" {
  role       = aws_iam_role.serverless_lambda.name
  policy_arn = aws_iam_policy.sagemaker_s3_policy.arn
}

# Attach Lambda basic execution role for CloudWatch Logs
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.serverless_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "serverless_lambda" {
  function_name = "cm3070-ml-serverless-lambda"
  role          = aws_iam_role.serverless_lambda.arn

  # Use container image instead of ZIP deployment
  package_type = "Image"
  image_uri    = "${aws_ecr_repository.cm3070_ml.repository_url}@${data.aws_ecr_image.cm3070_ml.image_digest}"

  architectures = ["arm64"]

  environment {
    variables = {
      STAGE = "dev"
    }
  }

  timeout     = 120
  memory_size = 2048

  ephemeral_storage {
    size = 3072 # Min 512 MB and the Max 10240 MB
  }

  tags = {
    Service = "serverless"
  }
}

# Lambda permission to allow S3 to invoke the function
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.serverless_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.cm3070_ml.arn
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.serverless_lambda.function_name}"
  retention_in_days = 14
}
