import json

import serial
import requests
import sys
import os

def print_usage():
    print('Usage: {} <ip> <port>'.format(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)
    serial_path = '' 
    for f in os.listdir('/dev/'):
        if f.startswith('tty.usbserial-'):
            serial_path = '/dev/' + f
            print('Using usb device at ' + serial_path)

    if len(serial_path) == 0 or not os.path.exists(serial_path):
        print("Unable to find a serial usb device.")
        sys.exit(1)

    port = serial.Serial(serial_path, baudrate=115200, timeout=3.0)

    while True:
        try:
            out = port.readline().decode("utf-8").strip()
            print('Received: ' + out)
            if out != "":
                if len(out) > 30:
                    raw = out[out.find("'")+1:out.rfind("'")].split()

                    ip = sys.argv[1]
                    http_port = sys.argv[2]
                    if raw[0] == "hello":
                        if len(raw) == 2:
                            data = {'dev_id': '0815',
                                    'payload_fields': {"height": float(raw[1])}}
                            json_string = json.dumps(data)
                            print(json_string)

                            r = requests.post(url="http://"+ip+":"+http_port+"/sensor/add_measurement", data=json_string)
                            

        except Exception as i:
            print(str(i))
