import os
import pytest

from dotenv import load_dotenv
import boto3


from functions.get_data.app import GetData

load_dotenv()


@pytest.fixture()
def get_event_body():
    return {
        "version": "0",
        "id": "8c0d884d-78c9-9217-1b6a-90c4560fba9c",
        "detail-type": "Object Created",
        "source": "aws.s3",
        "account": "233369945976",
        "time": "2022-11-16T22:02:21Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:s3:::stori-flow"
        ],
        "detail": {
            "version": "0",
            "bucket": {
                "name": "stori-flow"
            },
            "object": {
                "key": "10_vidanilo10@gmail.com.csv",
                "size": 73,
                "etag": "ba2a38101febc2fce18d687ee4a2bd82",
                "sequencer": "0063755DED1C836741"
            },
            "request-id": "60QECKC5F5MRGDKJ",
            "requester": "233369945976",
            "source-ip-address": "190.252.132.93",
            "reason": "PutObject"
        }
    }


@pytest.fixture()
def start_boto3_client():
    return boto3.client(
        service_name="s3",
        region_name=os.getenv("REGION"),
        AWS_ACCESS_KEY_ID_USER=os.getenv("ACCESS_KEY"),
        AWS_SECRET_ACCESS_KEY_USER=os.getenv("SECRET_KEY")
    )


@pytest.fixture
def upload_file(start_boto3_client):
    try:
        start_boto3_client.put_object(
            'tests/get_data/10_vidanilo10@gmail.com.csv',
            os.getenv("BUCKET"),
            '10_vidanilo10@gmail.com.csv'
        )
    except Exception as e:
        raise e


@pytest.fixture()
def starting_get_data(get_event_body):
    get_data = GetData(event=get_event_body)
    return get_data


def test_get_file_object(starting_get_data):
    assert starting_get_data.get_file_object()


def test_get_transactions(starting_get_data):
    assert starting_get_data.get_transactions()


def test_get_data(starting_get_data):
    assert starting_get_data.get_data()
