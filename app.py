#!/usr/bin/env python2.7

import sys
import time
import c4r  # Lib to send and receive commands

# load w1 modules
c4r.modprobe('w1-gpio')
c4r.modprobe('w1-therm')


# Put your device token here. To get a device token, register at http://stage.cloud4rpi.io
DeviceToken = 'YOUR_DEVICE_TOKEN'

c4r.set_device_token(DeviceToken)
cpu = c4r.find_cpu()

ds_sensors = c4r.find_ds_sensors()
print 'SENSORS FOUND ', ds_sensors


def bind_sensor(sensors, index):
    if not sensors is None and len(sensors) > index:
        return sensors[index]
    return None


def cooler_control(value=None):
    print 'New Cooler value: {0}'.format(value)
    return 42

# Put required variable declaration here
Variables = {
    'CurrentTemp_1': {
        'title': 'Temp sensor 1 reading',
        'type': 'numeric',
        'bind': bind_sensor(ds_sensors, 0)
    },
    'CurrentTemp_2': {
        'title': 'Temp sensor 2 reading',
        'type': 'numeric',
        'bind': bind_sensor(ds_sensors, 1)
    },
    'CoolerOn': {
        'title': 'Cooler enabled',
        'type': 'bool',
        'value': False,
        'bind': cooler_control
    },
    'CPU': {
        'title': 'CPU temperature',
        'type': 'numeric',
        'bind': cpu
    }
}


def main():
    c4r.register(Variables)  # Send variable declarations to server
    try:
        while True:
            c4r.read_persistent(Variables)  # Reads values from persistent memory, sensors
            c4r.read_system(Variables)  # Reads CPU temperature

            server_msg = c4r.send_receive(Variables)
            print 'Server message: {0}'.format(server_msg)
            c4r.process_variables(Variables, server_msg)
            time.sleep(5)

    except Exception as e:
        error = c4r.get_error_message(e)
        print "error", error, sys.exc_info()[0]
        raise

if __name__ == '__main__':
    main()
