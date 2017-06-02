# -*- coding: utf-8 -*-

import sys
import time
import RPi.GPIO as GPIO  # pylint: disable=F0401
import cloud4rpi

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 30  # secs
POLL_INTERVAL = 0.5  # 500 ms


# configure GPIO library
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)


# handler for the button or switch variable
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    return GPIO.input(LED_PIN)


def main():
    # Put variable declarations here
    variables = {
        'LEDOn': {
            'type': 'bool',
            'value': False,
            'bind': led_control
        }
    }
    device = cloud4rpi.Device()
    device.declare(variables)

    api = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    api.on_command = device.handle_mqtt_commands(api)

    cfg = device.read_config()
    api.publish_config(cfg)

    # Adds a 1 second delay to ensure device variables are created
    time.sleep(1)

    try:
        data_timer = 0
        while True:
            if data_timer <= 0:
                data = device.read_data()
                api.publish_data(data)
                data_timer = DATA_SENDING_INTERVAL

            time.sleep(POLL_INTERVAL)
            data_timer -= POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
