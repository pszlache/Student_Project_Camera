import os
import termios
import time
import select


class GSMClient:

    def __init__(self, port):

        self.port = port
        self.fd = None
        self.connected = False


    # ================= CONNECT =================

    def connect(self):

        print(f"[GSM] Opening modem {self.port}")

        self.fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)

        attrs = termios.tcgetattr(self.fd)

        # speed
        attrs[4] = termios.B115200
        attrs[5] = termios.B115200

        # enable receiver
        attrs[2] |= termios.CLOCAL | termios.CREAD

        # raw mode
        attrs[3] = 0
        attrs[1] = 0
        attrs[0] = 0

        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)

        # flush buffers
        termios.tcflush(self.fd, termios.TCIOFLUSH)

        time.sleep(2)

        self.connected = True

        self._init_sms()


    # ================= READ =================

    def _read(self, timeout=2):

        buffer = b""
        start = time.time()

        while time.time() - start < timeout:

            r, _, _ = select.select([self.fd], [], [], 0.2)

            if self.fd in r:

                chunk = os.read(self.fd, 1024)

                if chunk:
                    buffer += chunk

        return buffer.decode(errors="ignore")


    # ================= COMMAND =================

    def _send_command(self, cmd, delay=0.5):

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

        while time.time() - start < timeout:

            r, _, _ = select.select([self.fd], [], [], 0.2)

            if self.fd in r:

                data = os.read(self.fd, 1024).decode(errors="ignore")

                if data:
                    buffer += data

                    if ">" in buffer:
                        return

        raise Exception("No SMS prompt")


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

        time.sleep(4)

        resp = self._read()

        print("[GSM] Response:", resp)

        return resp


    # ================= CLOSE =================

    def close(self):

        if self.fd:

            print("[GSM] Closing modem")

            os.close(self.fd)

            self.connected = False