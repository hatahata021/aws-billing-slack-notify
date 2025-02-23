# Pythonの依存関係をインストールしてZip化
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/app.zip"
  source_dir  = "${path.module}/lambda_package"

  depends_on = [null_resource.install_dependencies]
}

# 依存関係のインストール
resource "null_resource" "install_dependencies" {
  triggers = {
    dependencies_versions = filemd5("${path.module}/requirements.txt")
    source_versions      = filemd5("${path.module}/app.py")
  }

  provisioner "local-exec" {
    command = <<EOF
      rm -rf ${path.module}/lambda_package
      mkdir -p ${path.module}/lambda_package
      pip install --target ${path.module}/lambda_package -r ${path.module}/requirements.txt
      cp ${path.module}/app.py ${path.module}/lambda_package/
    EOF
  }
}

# Lambda関数
resource "aws_lambda_function" "billing_notify" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "billing_slack_notify_function"
  role               = aws_iam_role.billing_lambda_role.arn
  handler            = "app.lambda_handler"
  runtime            = "python3.8"
  timeout            = 10

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.SLACK_WEBHOOK_URL
      SLACK_USER_ID     = var.SLACK_USER_ID
      AWS_ACCOUNT_ID    = var.AWS_ACCOUNT_ID
    }
  }
}

# Lambda関数のEventBridge呼び出し許可
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.billing_notify.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_billing_check.arn
}