import serial
import time


class GSMClient:

    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = None


    def connect(self):

        print(f"[GSM] Opening serial {self.port}")

        self.ser = serial.Serial(
            self.port,
            self.baudrate,
            timeout=1
        )

        time.sleep(3)

        # handshake
        for _ in range(5):

            response = self._send_command("AT", delay=1)

            if "OK" in response:
                print("[GSM] Modem ready")
                break

            time.sleep(1)

        # verbose errors
        self._send_command("AT+CMEE=2")

        # SMS text mode
        self._send_command("AT+CMGF=1")

        print("[GSM] SMS mode enabled")


    def _send_command(self, command, delay=0.5):

        self.ser.reset_input_buffer()

        self.ser.write((command + "\r").encode())

        time.sleep(delay)

        response = ""

        while self.ser.in_waiting:
            response += self.ser.read(self.ser.in_waiting).decode(errors="ignore")

        return response


    def send_sms(self, number, message):

        print(f"[GSM] Sending SMS to {number}")

        # start SMS command
        self.ser.write(f'AT+CMGS="{number}"\r'.encode())

        buffer = ""
        start = time.time()

        # wait for '>' prompt
        while ">" not in buffer:

            if time.time() - start > 5:
                raise TimeoutError("GSM modem did not return '>' prompt")

            buffer += self.ser.read(self.ser.in_waiting or 1).decode(errors="ignore")

        # send message
        self.ser.write(message.encode())

        time.sleep(0.3)

        # CTRL+Z
        self.ser.write(b'\x1A')

        time.sleep(5)

        response = self.ser.read_all().decode(errors="ignore")

        print(f"[GSM] Response: {response}")

        return response


    def close(self):

        if self.ser:
            self.ser.close()