# 本ソースコードは以下のブログを参考に、通知先をslackに変更したものです。
# 加えて、クレジット適用前の請求額を取得するように変更しています。
# https://dev.classmethod.jp/articles/notify-line-aws-billing/

import os
import boto3
import json
import requests
from datetime import datetime, timedelta, date

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
SLACK_USER_ID = os.environ["SLACK_USER_ID"]
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]


def lambda_handler(event, context) -> None:
    client = boto3.client('ce', region_name='us-east-1')

    # 合計とサービス毎の請求額を取得する
    total_billing = get_total_billing(client)
    service_billings = get_service_billings(client)
    uncredit_billing = get_uncredit_billing(client)

    # Slack用のメッセージを作成して投げる
    (title, detail) = get_message(total_billing, service_billings, uncredit_billing)
    post_slack(title, detail)


def get_total_billing(client) -> dict:
    (start_date, end_date) = get_total_cost_date_range()

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ]
    )
    return {
        'start': response['ResultsByTime'][0]['TimePeriod']['Start'],
        'end': response['ResultsByTime'][0]['TimePeriod']['End'],
        'billing': response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount'],
    }


def get_service_billings(client) -> list:
    (start_date, end_date) = get_total_cost_date_range()

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    billings = []

    for item in response['ResultsByTime'][0]['Groups']:
        billings.append({
            'service_name': item['Keys'][0],
            'billing': item['Metrics']['AmortizedCost']['Amount']
        })
    return billings


def get_uncredit_billing(client) -> str:
    client = boto3.client('budgets', region_name='us-east-1')
    
    try:        
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/budgets/client/describe_budget.html
        response = client.describe_budget(
            AccountId=AWS_ACCOUNT_ID,
            BudgetName='alert_$10_slack_notify_association'
        )

        print(response)

        # 実際のコスト（クレジット適用前）を取得
        actual_spend = float(response['Budget']['CalculatedSpend']['ActualSpend']['Amount'])
        return str(actual_spend)
        
    except Exception as e:
        print(f"Error getting budget information: {e}")
        return "0.0"  # エラーの場合はデフォルト値を返す


def get_message(total_billing: dict, service_billings: list, uncredit_billing: str) -> (str, str, str):
    start = datetime.strptime(total_billing['start'], '%Y-%m-%d').strftime('%m/%d')

    # Endの日付は結果に含まないため、表示上は前日にしておく
    end_today = datetime.strptime(total_billing['end'], '%Y-%m-%d')
    end_yesterday = (end_today - timedelta(days=1)).strftime('%m/%d')

    total = round(float(total_billing['billing']), 2)
    credit = round(float(uncredit_billing), 2)

    title = f'<@{SLACK_USER_ID}>\n{start}～{end_yesterday}の請求額は {total:.2f} USDです。\nクレジット適用前の金額は {credit:.2f} USDです。'

    details = []
    for item in service_billings:
        service_name = item['service_name']
        billing = round(float(item['billing']), 2)

        if billing == 0.0:
            # 請求無し（0.0 USD）の場合は、内訳を表示しない
            continue
        details.append(f'　・{service_name}: {billing:.2f} USD')

    return title, '\n'.join(details)


def post_slack(title: str, detail: str) -> None:
    # https://api.slack.com/incoming-webhooks
    # https://api.slack.com/docs/message-formatting
    # https://api.slack.com/docs/messages/builder

    payload = {
        'attachments': [
            {
                'color': '#36a64f',
                'pretext': title,
                'text': detail,
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        print(response.status_code)


def get_total_cost_date_range() -> (str, str):
    start_date = get_begin_of_month()
    end_date = get_today()

    # get_cost_and_usage()のstartとendに同じ日付は指定不可のため、
    # 「今日が1日」なら、「先月1日から今月1日（今日）」までの範囲にする
    if start_date == end_date:
        end_of_month = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=-1)
        begin_of_month = end_of_month.replace(day=1)
        return begin_of_month.date().isoformat(), end_date
    return start_date, end_date


def get_begin_of_month() -> str:
    return date.today().replace(day=1).isoformat()


def get_prev_day(prev: int) -> str:
    return (date.today() - timedelta(days=prev)).isoformat()


def get_today() -> str:
    return date.today().isoformat()