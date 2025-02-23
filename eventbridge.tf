# EventBridgeルール（旧CloudWatchEvents）
resource "aws_cloudwatch_event_rule" "daily_billing_check" {
  name                = "daily_slack_billing_check"
  description         = "Trigger Lambda function daily"
  schedule_expression = "cron(0 0 * * ? *)"
}

# EventBridgeターゲット
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_billing_check.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.billing_notify.arn
}