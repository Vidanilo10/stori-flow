import os
import pytest

from dotenv import load_dotenv
import boto3
import pandas as pd

from functions.process_data.app import ProcessData

load_dotenv()


@pytest.fixture()
def start_dynamodb_resource():
    return boto3.resource(
        service_name="dynamodb",
        region_name=os.getenv("REGION"),
        AWS_ACCESS_KEY_ID_USER=os.getenv("ACCESS_KEY"),
        AWS_SECRET_ACCESS_KEY_USER=os.getenv("SECRET_KEY")
    )


@pytest.fixture
def create_test_table(start_dynamodb_resource):
    start_dynamodb_resource.create_table(
        TableName=os.getenv("TABLE_NAME"),
        KeySchema=[
            {
                'AttributeName': 'Id',
                'KeyType': 'N'
            }
        ]
    )


@pytest.fixture()
def get_event_body():
    return {
        "account_id": 10,
        "email": "vidanilo10@gmail.com",
        "file_name": "vidanilo10@gmail.com.csv"
    }


@pytest.fixture()
def starting_process_data(get_event_body):
    process_data = ProcessData(event=get_event_body)
    return process_data


@pytest.fixture()
def get_data_frame():
    df = pd.DataFrame([
        {"id": 0, "date": "7/15", "transaction": float("+60.5")},
        {"id": 1, "date": "7/28", "transaction": float("-10.3")},
        {"id": 2, "date": "8/2", "transaction": float("-20.46")},
        {"id": 3, "date": "8/13", "transaction": float("+10")}
    ])
    pd.to_datetime(df['date'], format='%m/%d')
    return df


def test_get_total_balance(starting_process_data, get_data_frame):
    assert starting_process_data.get_total_balance(df=get_data_frame)

def test_get_transactions_by_month(starting_process_data, get_data_frame):
    assert starting_process_data.get_transactions_by_month(df=get_data_frame)

def test_get_average_debit_amount(starting_process_data, get_data_frame):
    assert starting_process_data.get_average_debit_amount(df=get_data_frame)

def test_get_average_credit_amount(starting_process_data, get_data_frame):
    assert starting_process_data.get_average_credit_amount(df=get_data_frame)