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


DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.1  # 100 ms


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

    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    try:
        while True:
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
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
