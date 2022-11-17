from datetime import datetime
import os
import json

import boto3


def lambda_handler(event, context):
    return GetData(event=event).handler()


class GetData:
    def __init__(self, event) -> None:
        self.dynamodb_table = boto3.resource(
            service_name="dynamodb",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        ).Table('account-table')

        self.s3_client = boto3.client(
            service_name="s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        )
        self.account_id = int(event.get("detail").get("object").get("key").split("_")[0])
        self.file_name = event.get("detail").get("object").get("key")
        self.user_email = str(event.get("detail").get("object").get("key").split("_")[1]).replace(".csv", "")
        self.transactions = self.get_transactions()

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
            api_exception_obj = {
                "isBase64Encoded": False,
                "StatusCode": 400,
                "Payload": json.dumps({
                    "error": {
                        "message": str(e),
                    }
                })
            }
            return api_exception_obj
        else:
            return {
                "account_id": self.account_id,
                "file_name": self.file_name,
                "email": self.user_email
            }
