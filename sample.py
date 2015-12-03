#!/usr/bin/env python2.7

import sys
import time
import c4r      #Lib to send and receive commands

# Put your device token here. To get a device token, register at http://stage.cloud4rpi.io
DeviceToken = "YOUR_DEVICE_TOKEN"

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
    try:
        while True:
            c4r.read_persistent(Variables) #reads values from persistent memory, sensors

            #c4r.process_variables([Variables['CurrentTemp']]) #reads values from persistent memory, sensors

            time.sleep(10)
    except:
        print "error", sys.exc_info()[0]
        raise

if __name__ == '__main__':
    main()
