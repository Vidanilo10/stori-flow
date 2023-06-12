import os
import boto3


def lambda_handler(event, context):
    return SendEmail(event=event).handler()


class SendEmail:
    def __init__(self, event):
        self.account_id = event.get("account_id")
        self.user_email = event.get("email")
        self.file_name = event.get("file_name")
        self.data = event.get("data")
        self.ses_client = start_ses_client()

    @staticmethod
    def start_ses_client():
        return boto3.client(
            service_name="ses",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID_USER"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY_USER")
        )

    def get_months_data(self):
        lines = []
        for t in self.data.get("transactions_by_month"):
            for key in t:
                lines.append(f"Number of transactions in {key}: {t[key]}")
        return '\n'.join(lines)

    def get_html_content(self):
        html_content = f"""
            <html>
                <head></head>
                </body
                    <h1 style='text-align:center'>Stori Transactions report</h1>
                    <br>
                    <p>
                        Hello, dear user, we have excellent news for you. There is your transactions
                        report with the resume and the necessary values to analyze your activity over owr
                        application. 
                    </p>
                    <br>
                    <h2 style='text-align:center'> Data </h2>
                    <br>
                    <h4>Total balance: {self.data.get("total_balance")}</h4>
                    <h4>Average debit amount: {self.data.get("average_debit_amount")}</h4>
                    <h4>Average credit amount: {self.data.get("average_credit_amount")}</h4>
                    <h4>Data by months: </h4>
                    <h4>{self.get_months_data()}</h4>
                    <br>
                    <p>
                        Thanks a lot dear user, This is the stori communications team. 
                    </p>
                    <p>
                        Please take your time to analyze the information. If you have doubts feel free 
                        to contact our support team.
                    </p>
                    <div style="text-align: left;">
                        <img src="https://blog.storicard.com/wp-content/uploads/2019/07/Stori-horizontal-11.jpg" alt="stori_image", width="600"> 
                    </div>
                </body>
            </html>
        """
        return html_content

    def send_email(self):
        self.ses_client.send_email(
            Destination={
                "ToAddresses": [
                    self.user_email,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": "UTF-8",
                        "Data": self.get_html_content(),
                    }
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": "Transactions report",
                },
            },
            Source=self.user_email,
        )

    def handler(self):
        try:
            self.send_email()
        except Exception as e:
            raise e
        else:
            return {
                "account_id": self.account_id,
                "email": self.user_email,
                "file_name": self.file_name
            }
