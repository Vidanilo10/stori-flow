import os

import boto3

def lambda_handler(event, context):
    get_data = GetData(event=event)

class GetData:
    def __init__(self, event) -> None:
        self.dynamodb_client = boto3.client("dynamodb")
        self.s3_client = boto3.client("s3")
        self.account_id = event.get("file_name")
        self.file_name = event.get("file_name")
        self.get_transactions = self.__get_transactions()

    def __get_transactions(self):
        response = self.s3_client.get_object(
            Bucket=os.getenv["BUCKET"],
            Key=self.file_name
        )
        
        transactions = []
        for i, line in enumerate(response['Body'].iter_lines()):
            line.decode('utf-8')
            transactions.append({
                "id": line[0],
                "Date": line[1],
                "Transaction": line[2]
            })

        return transactions

    def query_object(self):
        response = self.dynamodb_client.get_item(
            TableName=os.getenv['TABLE_NAME'],
            Key=self.account_id
        )
        
        if response:
            self.dynamodb_client.update_item(
                TableName=os.getenv['TABLE_NAME'],
                Key=self.account_id,
                AttributeUpdates={
                    "Transactions": self.__get_transactions()
                }
            )
        else:
            self.dynamodb_client.put_item(
                TableName=os.getenv['TABLE_NAME'],
                Item={
                    "Id": self.account_id,
                    "Transactions": self.__get_transactions()
                }
            )
