#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
import time
import cloud4rpi
from examples.raspberrypi.lib import gpio

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 30  # secs
POLL_INTERVAL = 0.5  # 500 ms


# use output GPIO pin
ledOn = gpio.GpioActuator(LED_PIN)
print('ACTUATOR_____', ledOn)


# handler for the button or switch variable
def led_control(value=None):
    cloud4rpi.log.error("User-function called with (%s)", value)
    return ledOn.set(value)


def main():
    # Put variable declarations here
    variables = {
        'LEDOn': {
            'type': 'bool',
            'value': False,
            'bind': led_control
        }
    }

    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare(variables)
    device.send_data()

    try:
        time_passed = 0
        next_data_sending = DATA_SENDING_INTERVAL
        while True:
            if time_passed >= next_data_sending:
                next_data_sending += DATA_SENDING_INTERVAL
                device.send_data()

            time.sleep(POLL_INTERVAL)
            time_passed += POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
