# Lambda用のIAMロール
resource "aws_iam_role" "billing_lambda_role" {
  name = "billing_slack_notify_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAMポリシー
resource "aws_iam_role_policy" "billing_lambda_policy" {
  name = "billing_slack_notify_lambda_policy"
  role = aws_iam_role.billing_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ce:GetCostAndUsage",
        "budgets:ViewBudget"
      ]
      Resource = "*"
    }]
  })
}