import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SMTPProvider:

    def __init__(self, host, port, username, password, use_ssl=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl

    def send(self, recipients, subject, body):

        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=10)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=10)
                server.starttls()

            server.login(self.username, self.password)

            server.sendmail(
                self.username,
                recipients,
                msg.as_string()
            )

            server.quit()

            print("[SMTP] Mail sent")

        except Exception as e:
            print(f"[SMTPProvider] SMTP error: {e}")
            raise