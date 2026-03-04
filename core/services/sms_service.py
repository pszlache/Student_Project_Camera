class SMSService:

    def __init__(self, gsm_client):
        self.gsm = gsm_client

    def send_sms(self, number, message):

        self.gsm.send_command("AT+CMGF=1")

        self.gsm.send_command(
            f'AT+CMGS="{number}"',
            expect=">"
        )

        self.gsm.send_raw(message + "\x1A")

        return "OK"