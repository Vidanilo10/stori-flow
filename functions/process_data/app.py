import calendar
import os

import pandas as pd
import boto3


def lambda_handler(event, context):
    return ProcessData(event=event).handler()


class ProcessData:
    def __init__(self, event):
        self.account_id = event.get("account_id")
        self.file_name = event.get("file_name")
        self.user_email = event.get("email")
        self.dynamodb_table = self.get_dynamodb_table()

    @staticmethod
    def get_dynamodb_table():
        return boto3.resource(
            service_name="dynamodb",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        ).Table('account-table')

    def get_item(self):
        resp = self.dynamodb_table.get_item(
            Key={
                "Id": int(self.account_id)
            }
        )
        return resp.get("Item").get("Transactions")

    def get_data_frame(self):
        df = pd.DataFrame(self.get_item())
        return df

    def update_data_frame(self) -> None:
        df = self.get_data_frame()
        df['date'] = pd.to_datetime(df['date'], format='%m/%d')
        df['id'] = df['id'].astype(int)
        df['transaction'] = df['transaction'].astype(float)
        self.df = df

    def get_data(self):
        return {
            "total_balance": self.get_total_balance(),
            "transactions_by_month": self.get_transactions_by_month(),
            "average_debit_amount": self.get_average_debit_amount(),
            "average_credit_amount": self.get_average_credit_amount()
        }

    def get_total_balance(self):
        return self.df['transaction'].sum()

    def get_transactions_by_month(self):
        group = self.df.groupby(df.date.dt.month)['date']
        return [{calendar.month_name[k]: len(v)} for k, v in group.groups.items()]

    def get_average_debit_amount(self):
        return self.df[self.df['transaction'] < 0]['transaction'].mean()

    def get_average_credit_amount(self):
        return self.df[self.df['transaction'] > 0]['transaction'].mean()

    def handler(self):
        try:
            data = self.get_data()
        except Exception as e:
            raise e
        else:
            return {
                "account_id": self.account_id,
                "email": self.user_email,
                "file_name": self.file_name,
                "data": data
            }
