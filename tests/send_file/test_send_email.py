import pytest

from functions.send_email.app import SendEmail


@pytest.fixture()
def get_event_body():
    return {
        "account_id": 10,
        "email": "vidanilo10@gmail.com",
        "file_name": "vidanilo10@gmail.com.csv",
        "data": {
            "total_balance": 39.74,
            "transactions_by_month": [
                {
                    "August": 2
                },
                {
                    "July": 2
                }
            ],
            "average_debit_amount": -15.38,
            "average_credit_amount": 35.25
        }
    }


@pytest.fixture()
def starting_send_email(get_event_body):
    send_email = SendEmail(event=get_event_body)
    return send_email


def test_get_months_data(starting_send_email):
    assert starting_send_email.get_months_data()


def test_get_html_content(starting_send_email):
    assert starting_send_email.get_html_content()


def test_send_email(starting_send_email):
    assert starting_send_email.send_email()
