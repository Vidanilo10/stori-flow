import os
import json

import boto3


def lambda_handler(event, context):
    return GetData(event=event).handler()


class GetData:
    def __init__(self, event) -> None:
        self.dynamodb_client = boto3.client(
            service_name="dynamodb",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        )
        self.s3_client = boto3.client(
            service_name="s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        )
        self.account_id = event.get("detail").get("object").get("key").split(".")[0]
        self.file_name = event.get("detail").get("object").get("key")
        self.get_transactions = self.get_transactions()

    def get_file_object(self):
        return self.s3_client.get_object(
            Bucket=os.environ.get("BUCKET"),
            Key=self.file_name
        )

    def get_transactions(self):
        transactions = []
        for i, line in enumerate(self.get_file_object()['Body'].iter_lines()):
            line.decode('utf-8')
            transactions.append({
                "id": line[0],
                "Date": line[1],
                "Transaction": line[2]
            })

        return transactions

    def query_object(self):
        return self.dynamodb_client.get_item(
            TableName=os.environ.get('TABLE_NAME'),
            Key=self.account_id
        )

    def put_item(self):
        self.dynamodb_client.put_item(
            TableName=os.environ.get('TABLE_NAME'),
            Item={
                "Id": self.account_id,
                "Transactions": self.get_transactions()
            }
        )

    def update_item(self):
        self.dynamodb_client.update_item(
            TableName=os.environ.get('TABLE_NAME'),
            Key=self.account_id,
            AttributeUpdates={
                "Transactions": self.get_transactions()
            }
        )

    def get_data(self):
        if self.query_object():
            self.update_item()
        else:
            self.put_item()

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
                "file_name": self.file_name
            }
