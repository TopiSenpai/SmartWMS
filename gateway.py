import json

import serial
import requests
import sys

port = serial.Serial("/dev/tty.usbserial-14340", baudrate=115200, timeout=3.0)

while True:
    try:
        out = port.readline().decode("utf-8").strip()
        if out is not "":
            if len(out) > 30:
                raw = out[out.find("'")+1:out.rfind("'")].split()

                ip = sys.argv[1]
                http_port = sys.argv[2]
                if raw[0] == "hello":
                    if len(raw) == 2:
                        data = {'dev_id': raw[0],
                                'payload_fields': {"height": float(raw[1])}}
                        json_string = json.dumps(data)
                        print(json_string)

                        r = requests.post(url="http://"+ip+":"+http_port+"/sensor/add_measurements", data=json_string)

    except Exception as i:
        print(str(i))
