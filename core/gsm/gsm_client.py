import serial
import time


class GSMClient:

    def __init__(self, port, baudrate):

        self.port = port
        self.baudrate = baudrate
        self.ser = None

        self.connected = False

    # ================= CONNECT =================

    def connect(self):

        print(f"[GSM] Opening serial {self.port}")

        try:

            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                rtscts=False,
                dsrdtr=True,
                write_timeout=2
            )

            time.sleep(2)

            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            for _ in range(5):

                resp = self._send_command("AT")

                if "OK" in resp:
                    self.connected = True
                    print("[GSM] Modem ready")
                    break

                time.sleep(1)

            if not self.connected:
                raise Exception("GSM modem not responding")

            # SMS init
            self._send_command("AT+CMEE=2")
            self._send_command("AT+CSMS=1")
            self._send_command("AT+CMGF=1")
            self._send_command('AT+CSCS="GSM"')

            print("[GSM] SMS service initialized")

        except Exception as e:

            print("[GSM] Connect error:", e)
            self.connected = False
            raise

    # ================= COMMAND =================

    def _send_command(self, command, delay=0.5):

        if not self.ser:
            raise Exception("Serial not open")

        self.ser.write((command + "\r").encode())

        time.sleep(delay)

        response = ""

        while self.ser.in_waiting:
            response += self.ser.read(self.ser.in_waiting).decode(errors="ignore")

        return response

    # ================= NETWORK =================

    def check_network(self):

        resp = self._send_command("AT+CEREG?")

        if ",1" in resp or ",5" in resp:
            return True

        return False

    # ================= SEND SMS =================

    def send_sms(self, number, message, retries=3):

        for attempt in range(retries):

            try:

                if not self.connected:
                    print("[GSM] Reconnecting modem")
                    self.connect()

                if not self.check_network():
                    raise Exception("Modem not registered in network")

                print(f"[GSM] Sending SMS to {number}")

                # start SMS
                self.ser.write(f'AT+CMGS="{number}"\r'.encode())

                buffer = ""
                start = time.time()

                while ">" not in buffer:

                    if time.time() - start > 5:
                        raise TimeoutError("No '>' prompt")

                    if self.ser.in_waiting:
                        buffer += self.ser.read(self.ser.in_waiting).decode(errors="ignore")

                # message
                self.ser.write(message.encode())

                time.sleep(0.2)

                # CTRL+Z
                self.ser.write(b"\x1A")

                time.sleep(4)

                response = ""

                while self.ser.in_waiting:
                    response += self.ser.read(self.ser.in_waiting).decode(errors="ignore")

                print("[GSM] Response:", response)

                if "OK" in response or "+CMGS" in response:
                    return True

                raise Exception("SMS send failed")

            except Exception as e:

                print(f"[GSM] SMS attempt {attempt+1} failed:", e)

                self.connected = False

                time.sleep(2)

        print("[GSM] SMS sending failed after retries")

        return False

    # ================= CLOSE =================

    def close(self):

        if self.ser:

            print("[GSM] Closing modem")

            self.ser.close()

            self.connected = False