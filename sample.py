#!/usr/bin/env python2.7

import sys
import time
import c4r      #Lib to send and receive commands

# Put your device token here. To get a device token, register at http://stage.cloud4rpi.io
DeviceToken = "562dd4892bb8a6b635797c15"

c4r.set_device_token(DeviceToken)
ds_sensors = c4r.find_ds_sensors()

print 'SENSORS FOUND ', ds_sensors

Variables = {
    'CurrentTemp': {
        'title': 'Temp sensor reading',
        'type': 'numeric',
        'bind': ds_sensors[0]
    }
}

def main():

    c4r.register(Variables)
    try:
        while True:
            c4r.read_persistent(Variables) #reads values from persistent memory, sensors
            c4r.send_receive(Variables)

    except Exception as e:
        error = c4r.get_error_message(e)
        print "error", error, sys.exc_info()[0]
        raise

if __name__ == '__main__':
    main()
