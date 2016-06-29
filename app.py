#!/usr/bin/env python2.7

import sys
import signal
import time
from threading import Timer
import c4r  # Lib to send and receive commands

try:
    import RPi.GPIO as GPIO  # pylint: disable=F0401

    gpio_loaded = True
except Exception as e:
    print 'Warning! No RPi.GPIO loaded!'
    gpio_loaded = False

# load w1 modules
c4r.modprobe('w1-gpio')
c4r.modprobe('w1-therm')


# Put your API key here. To get a token, register at https://cloud4rpi.io
API_KEY = 'YOUR_ACCESS_TOKEN'
c4r.set_api_key(API_KEY)

cpu = c4r.find_cpu()
ds_sensors = c4r.find_ds_sensors()
print 'SENSORS FOUND ', ds_sensors


def bind_sensor(sensors, index):
    if sensors is not None and len(sensors) > index:
        return sensors[index]
    return None


led_pin = 12
if gpio_loaded:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(led_pin, GPIO.OUT)


def led_control(value=None):
    GPIO.output(led_pin, value)
    return GPIO.input(led_pin)


# Put required variable declaration here
Variables = {
    # 'CurrentTemp_1': {
    #     'type': 'numeric',
    #     'bind': bind_sensor(ds_sensors, 0)
    # },
    #
    # 'CurrentTemp_2': {
    #     'type': 'numeric',
    #     'bind': bind_sensor(ds_sensors, 1)
    # },
    #
    'LEDOn': {
        'type': 'bool',
        'value': False,
        'bind': led_control
    },

    'CPU': {
        'type': 'numeric',
        'bind': cpu
    }
}


SEND_DIAGNOSTIC_TIMEOUT_IN_SEC = 60


def start_send_system_data():
    c4r.send_system_info()
    Timer(SEND_DIAGNOSTIC_TIMEOUT_IN_SEC, start_send_system_data).start()


def signal_handler():
    print 'Keyboard interrupt received. Stopping...'
    c4r.finalize()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def main():

    c4r.start_message_broker_listen()  # Receives control commands from server
    c4r.register(variables=Variables)  # Sends variable declarations to server

    start_send_system_data()    # Sends system diagnostic data to server every 60 sec
    try:
        while True:
            c4r.read_variables(Variables)  # Reads bounded values from persistent memory, sensors
            c4r.send_receive(Variables)  # Sends variable values data to server

            time.sleep(10)

    except Exception as e:
        error = c4r.get_error_message(e)
        print "error", error, sys.exc_info()[0]
        c4r.finalize()
        raise


if __name__ == '__main__':
    main()
