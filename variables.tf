variable "SLACK_WEBHOOK_URL" {
  description = "Slack Webhook URL for notifications"
  type        = string
}

variable "SLACK_USER_ID" {
  description = "Slack User ID for mentions"
  type        = string
} 

variable "AWS_ACCOUNT_ID" {
  description = "AWS Account ID"
  type        = string
}

variable "SUBSCRIBER_EMAIL_ADDRESSES" {
  description = "Subscriber Email Addresses"
  type        = list(string)
}
