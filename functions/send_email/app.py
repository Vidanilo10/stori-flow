from datetime import datetime
from random import randint
from uuid import uuid4


def lambda_handler(event, context):
    return {
        "greeting": "send_email"
    }
