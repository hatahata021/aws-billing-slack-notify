resource "aws_budgets_budget" "cost_alert" {
  name              = "alert_$10_slack_notify_association"
  budget_type       = "COST"
  limit_amount      = "10"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type           = "PERCENTAGE"
    notification_type        = "ACTUAL"
    subscriber_email_addresses = var.SUBSCRIBER_EMAIL_ADDRESSES
  }

  cost_types {
    include_credit             = false
    include_discount          = true
    include_other_subscription = true
    include_recurring         = true
    include_refund           = false
    include_subscription     = true
    include_support          = true
    include_tax             = true
    include_upfront         = true
    use_amortized          = false
    use_blended            = false
  }
}