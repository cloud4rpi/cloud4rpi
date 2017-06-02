# -*- coding: utf-8 -*-

import sys
import time
import cloud4rpi


# these functions will be called by device when sending data
def room_temp():
    return 25


def outside_temp():
    return 4


def cpu_temp():
    return 70


def ip_address():
    return '8.8.8.8'


def hostname():
    return 'hostname'


def osname():
    return 'osx'

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.5  # 500 ms


def main():
    # Put variable declarations here
    variables = {
        'RoomTemp': {
            'type': 'numeric',
            'bind': room_temp
        },
        'OutsideTemp': {
            'type': 'numeric',
            'bind': outside_temp
        }
    }

    # Put system data declarations here
    diagnostics = {
        'CPUTemp': cpu_temp,
        'IPAddress': ip_address,
        'Host': hostname,
        'OS Name': osname
    }

    device = cloud4rpi.Device()
    device.declare(variables)
    device.declare_diag(diagnostics)

    api = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    cfg = device.read_config()
    api.publish_config(cfg)

    # Adds a 1 second delay to ensure device variables are created
    time.sleep(1)

    try:
        diag_timer = 0
        data_timer = 0
        while True:
            if data_timer <= 0:
                data = device.read_data()
                api.publish_data(data)
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                diag = device.read_diag()
                api.publish_diag(diag)
                diag_timer = DIAG_SENDING_INTERVAL

            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
