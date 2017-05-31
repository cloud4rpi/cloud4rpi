# -*- coding: utf-8 -*-

import sys
import time
import json
import random

import cloud4rpi

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
DATA_SENDING_INTERVAL = 10  # secs
POLL_INTERVAL = 0.5  # 500 ms
LOG_FILE_PATH = 'cloud4rpi.log'

cloud4rpi.set_logging_to_file(LOG_FILE_PATH)

led_state = False


# handler for the button or switch variable
def led_control(value=None):
    global led_state  # pylint: disable=W0603
    if led_state != value:
        led_state = value
        cloud4rpi.log.info('LED state changed to %s', value)

    return led_state


def listen_for_events():
    # write your own logic here
    result = random.randint(1, 5)
    if result == 1:
        return 'RING'

    if result == 5:
        return 'BOOM!'

    return 'IDLE'


def log_response(func):
    def wrapper(*args):
        res = func(*args)
        cloud4rpi.log.info(res.status_code)
        return res

    return wrapper


@log_response
def publish_data(api, data):
    return api.publish_data(data)


@log_response
def publish_config(api, cfg):
    return api.publish_config(cfg)


@log_response
def fetch_commands(api):
    return api.fetch_commands()


def main():
    variables = {
        'STATUS': {
            'type': 'string',
            'bind': listen_for_events
        },

        'LEDOn': {
            'type': 'bool',
            'value': False,
            'bind': led_control
        },
    }

    device = cloud4rpi.Device()
    device.declare(variables)

    api = cloud4rpi.HttpApi(DEVICE_TOKEN)
    cfg = device.read_config()
    publish_config(api, cfg)

    try:
        data_timer = 0
        while True:
            if data_timer <= 0:
                res = fetch_commands(api)
                cmds = json.loads(res.content)
                for x in cmds:
                    cloud4rpi.log.info('Applying commands: %s', x)
                    device.apply_commands(x)

                data = device.read_data()
                publish_data(api, data)

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
