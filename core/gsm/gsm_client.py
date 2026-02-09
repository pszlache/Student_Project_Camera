import serial
import time

class GSMClient:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
    
    def connect(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        time.sleep(3)

        for _ in range(5):
            response = self._send_command("AT", delay=1)
            if "OK" in response:
                break
            time.sleep(1)

        self._send_command("AT+CMGF=1")  # Text mode

    def _send_command(self, command, delay=0.5):
        self.ser.write((command + "\r\n").encode())
        time.sleep(delay)
        return self.ser.read_all().decode(errors='ignore')
    
    def send_sms(self, number, message):
        self._send_command(f"AT+CMGS=\"{number}\"")
        self.ser.write((message + "\x1A").encode())
        time.sleep(3)  # Wait for message to send
        return self.ser.read_all().decode(errors='ignore')
    
    def close(self):
        if self.ser:
            self.ser.close()