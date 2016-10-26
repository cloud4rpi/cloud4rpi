#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# =============================================================================
# To run this sample,
# 1. git clone https://github.com/cloud4rpi/cloud4rpi.git && cd cloud4rpi
# 2. pip install -r requirements.txt
# 3. python examples/simple_mqtt_messaging.py
# =============================================================================

# This needed to be able to import the cloud4rpi directory from examples
if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

import os
import sys
import time
import cloud4rpi
import RPi.GPIO as GPIO  # pylint: disable=E0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '!!! put your device token here !!!'

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.1  # 100 ms


def configure_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)


# handler for the button or switch variable
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    current = GPIO.input(LED_PIN)
    return current


def main():
    configure_gpio()

    #  load w1 modules
    cloud4rpi.modprobe('w1-gpio')
    cloud4rpi.modprobe('w1-therm')

    # detect ds18b20 temperature sensors
    # ds_sensors = cloud4rpi.DS18b20.find_all()

    # Put variable declarations here
    variables = {
        # 'CurrentTemp_1': {
        #     'type': 'numeric',
        #     'bind': ds_sensors[0]
        # },

        # 'CurrentTemp_2': {
        #     'type': 'numeric',
        #     'bind': ds_sensors[1]
        # },

        'LEDOn': {
            'type': 'bool',
            'value': False,
            'bind': led_control
        },

        'CPUTemp': {
            'type': 'numeric',
            'bind': cloud4rpi.CpuTemperature()
        }
    }

    diagnostics = {
        'CPU Temperature': cloud4rpi.CpuTemperature(),
        'IPAddress': cloud4rpi.IPAddress(),
        'Host': cloud4rpi.Hostname(),
        'OS Name': ' '.join(str(x) for x in os.uname())
    }

    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    device.send_data()
    device.send_diag()

    try:
        time_passed = 0
        next_data_sending = DATA_SENDING_INTERVAL
        next_diag_sending = DIAG_SENDING_INTERVAL
        while True:
            if time_passed >= next_data_sending:
                next_data_sending += DATA_SENDING_INTERVAL
                device.send_data()

            if time_passed >= next_diag_sending:
                next_diag_sending += DIAG_SENDING_INTERVAL
                device.send_diag()

            time.sleep(POLL_INTERVAL)
            time_passed += POLL_INTERVAL

    except KeyboardInterrupt:
        print('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        print("ERROR! {0} {1}".format(error, sys.exc_info()[0]))

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
