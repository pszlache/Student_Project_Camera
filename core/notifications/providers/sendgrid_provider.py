from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .email_provider import EmailProvider


class SendGridProvider(EmailProvider):

    def __init__(self, api_key, from_email):
        self.client = SendGridAPIClient(api_key)
        self.from_email = from_email

    def send(self, recipients, subject, body):

        for recipient in recipients:

            message = Mail(
                from_email=self.from_email,
                to_emails=recipient,
                subject=subject,
                plain_text_content=body
            )

            self.client.send(message)