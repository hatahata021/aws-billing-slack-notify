# aws-billing-slack-notify

## 概要

以下2つの機能を実装しています。
1. AWSの請求額を定期的にSlackに通知するLambda関数
2. Budgetの設定をして、請求額が閾値を超えたらSlackに通知する機能

Lambda関数はクレジット適用前の月額を取得して通知しますが、そのためにはBudgetの設定が必要です。<br>
Budgetの通知が不要な場合は、Budgetのsubscription設定を解除してください。

## 事前準備

1. SlackのWebhook URLを取得する<br>
以下URLを参考に、SlackのWebhook URLを取得する（チャンネル名は適宜変更してください）
https://qiita.com/vmmhypervisor/items/18c99624a84df8b31008



2. SlackのユーザーIDを取得する<br>
参考：https://zenn.dev/shown_it/articles/4fdec84cba4034


## 作成方法

1. このリポジトリをクローンする

```bash
git clone https://github.com/aws-billing-slack-notify.git
```

2. リポジトリのルートディレクトリに移動する

```bash
cd aws-billing-slack-notify
```

3. terraform.tfvarsを作成する

```terraform.tfvars
SLACK_WEBHOOK_URL = "your_slack_webhook_url"
SLACK_USER_ID     = "your_slack_user_id"
AWS_ACCOUNT_ID    = "your_account_id"
SUBSCRIPTION_EMAIL_ADDRESS = ["your_email@example.com"]
```

4. terraformを実行する

```bash
terraform init
terraform plan
terraform apply
```



