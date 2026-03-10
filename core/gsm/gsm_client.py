import os
import termios
import time


class GSMClient:

    def __init__(self, port):

        self.port = port
        self.fd = None
        self.connected = False


    # ================= CONNECT =================

    def connect(self):

        print(f"[GSM] Opening modem {self.port}")

        self.fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY)

        attrs = termios.tcgetattr(self.fd)

        attrs[4] = termios.B115200
        attrs[5] = termios.B115200

        attrs[2] |= termios.CLOCAL | termios.CREAD

        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)

        time.sleep(2)

        self.connected = True

        self._init_sms()


    # ================= READ =================

    def _read(self):

        data = b""

        try:
            while True:
                chunk = os.read(self.fd, 1024)
                if not chunk:
                    break
                data += chunk
        except BlockingIOError:
            pass

        return data.decode(errors="ignore")


    # ================= COMMAND =================

    def _send_command(self, cmd, delay=1):

        print(">>>", cmd)

        os.write(self.fd, (cmd + "\r").encode())

        time.sleep(delay)

        resp = self._read()

        print(resp)

        return resp


    # ================= INIT SMS =================

    def _init_sms(self):

        self._send_command("AT")
        self._send_command("AT+CMEE=2")
        self._send_command("AT+CSMS=1")
        self._send_command("AT+CMGF=1")
        self._send_command('AT+CSCS="GSM"')

        print("[GSM] SMS initialized")


    # ================= WAIT PROMPT =================

    def _wait_prompt(self, timeout=10):

        buffer = ""
        start = time.time()

        while True:

            if time.time() - start > timeout:
                raise Exception("No SMS prompt")

            try:

                data = os.read(self.fd, 1024).decode(errors="ignore")

                if data:
                    buffer += data

                    if ">" in buffer:
                        return

            except BlockingIOError:
                pass

            time.sleep(0.1)


    # ================= SEND SMS =================

    def send_sms(self, number, message):

        if not self.connected:
            raise Exception("GSM not connected")

        print(f"[GSM] Sending SMS to {number}")

        os.write(self.fd, f'AT+CMGS="{number}"\r'.encode())

        self._wait_prompt()

        os.write(self.fd, message.encode())

        time.sleep(0.2)

        os.write(self.fd, b"\x1A")

        time.sleep(5)

        resp = self._read()

        print("[GSM] Response:", resp)

        return resp


    # ================= CLOSE =================

    def close(self):

        if self.fd:

            print("[GSM] Closing modem")

            os.close(self.fd)

            self.connected = False