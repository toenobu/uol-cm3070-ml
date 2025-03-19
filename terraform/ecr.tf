resource "aws_ecr_repository" "cm3070_ml" {
  name = "cm3070_ml"

  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "cm3070_ml_policy" {
  repository = aws_ecr_repository.cm3070_ml.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep only the 5 most recent images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["dev"],
          countType     = "imageCountMoreThan",
          countNumber   = 5
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
}

data "aws_ecr_image" "cm3070_ml" {
  repository_name = aws_ecr_repository.cm3070_ml.name
  most_recent     = true
}
