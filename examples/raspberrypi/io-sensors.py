#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import sys
import time
import cloud4rpi

from examples.raspberrypi.lib import ds18b20
from examples.raspberrypi.lib import rpi

import RPi.GPIO as GPIO  # pylint: disable=F0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.1  # 100 ms

log = logging.getLogger(cloud4rpi.config.loggerName)
log.setLevel(logging.INFO)


def configure_logging(logger):
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console)


def configure_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)


# handler for the button or switch variable
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    current = GPIO.input(LED_PIN)
    return current


def main():
    configure_logging(log)
    configure_gpio()

    # #  load w1 modules
    ds18b20.init_w1()

    # detect ds18b20 temperature sensors
    ds_sensors = ds18b20.DS18b20.find_all()

    # Put variable declarations here
    variables = {
        'CurrentTemp_1': {
            'type': 'numeric',
            'bind': ds_sensors[0]
        },

        # 'CurrentTemp_2': {
        #     'type': 'numeric',
        #     'bind': ds_sensors[1]
        # },

        'LEDOn': {
            'type': 'bool',
            'value': False,
            'bind': led_control
        },
        #
        # 'CPUTemp': {
        #     'type': 'numeric',
        #     'bind': rpi.cpu_temp() //TODO support for func
        # }
    }

    diagnostics = {
        'CPU Temperature': rpi.cpu_temp(),
        'IPAddress': rpi.ip_address(),
        'Host': rpi.hostname(),
        'OS Name': rpi.osname()
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
        log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
