from datetime import datetime
import os
import json

import boto3


def lambda_handler(event, context):
    return GetData(event=event).handler()


class GetData:
    def __init__(self, event) -> None:
        self.dynamodb_table = self.start_dynamodb_table()
        self.s3_client = self.start_s3_client()
        self.account_id = self.get_account_id(event=event)
        self.file_name = self.get_file_name(event=event)
        self.user_email = self.get_user_email(event=event)
        self.transactions = self.get_transactions()

    @staticmethod
    def start_dynamodb_table():
        return boto3.resource(
            service_name="dynamodb",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        ).Table('account-table')

    @staticmethod
    def start_s3_client():
        return boto3.client(
            service_name="s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        )

    @staticmethod
    def get_account_id(event):
        return int(event.get("detail").get("object").get("key").split("_")[0])

    @staticmethod
    def get_file_name(event):
        return event.get("detail").get("object").get("key")

    @staticmethod
    def get_user_email(event):
        return str(event.get("detail").get("object").get("key").split("_")[1]).replace(".csv", "")

    def get_file_object(self):
        return self.s3_client.get_object(
            Bucket=os.environ.get("BUCKET"),
            Key=self.file_name
        )

    def get_transactions(self):
        transactions = []
        lines = self.get_file_object()['Body'].read().decode("utf-8").split('\n')
        for line in lines[1:]:
            i = line.split(", ")
            transactions.append(
                {
                    "id": i[0],
                    "date": i[1],
                    "transaction": i[2].replace("\r", "")
                }
            )
        return transactions

    def get_data(self):
        self.dynamodb_table.update_item(
            Key={
                "Id": self.account_id
            },
            UpdateExpression="set #e=:e, #t=:t",
            ExpressionAttributeValues={":e": self.user_email, ":t": self.transactions},
            ExpressionAttributeNames={"#e": "Email", "#t": "Transactions"},
            ReturnValues="UPDATED_NEW",
        )

    def handler(self):
        try:
            self.get_data()
        except Exception as e:
            raise e
        else:
            return {
                "account_id": self.account_id,
                "file_name": self.file_name,
                "email": self.user_email
            }
