# -*- coding: utf-8 -*-

from os import uname
from socket import gethostname
from sys import exc_info
from time import sleep
import subprocess
import cloud4rpi

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

DATA_SENDING_INTERVAL = 30  # seconds


# find the path to the Omega LED
led_name = subprocess.check_output(["uci", "get", "system.@led[0].sysfs"])
led_brightness_path = "/sys/class/leds/%s/brightness" % (led_name.rstrip())


def omega_led(state):
    open(led_brightness_path, 'w').write('1' if state else '0')
    return bool(int(open(led_brightness_path, 'r').read()))

RGB_pins = {'R': '17', 'G': '16', 'B': '15'}  # Expansion board

# You can use onionGpio python module (if it is already working)
# https://docs.onion.io/omega2-docs/gpio-python-module.html#using-the-python-module-2

for _, pin in RGB.items():
    subprocess.call("gpioctl dirout-high " + pin, shell=True)


def RGB_control(led, value):
    operation = 'clear' if value else 'set'  # (sic)
    try:
        return not subprocess.call("gpioctl %s %s" %
                                   (operation, RGB_pins[led]), shell=True)
    except KeyError:
        return False


def RGB_check(led):
    return 'LOW' in str(subprocess.check_output(["gpioctl", "get",
                                                 RGB_pins[led]]))


def RED_control(state):
    if RGB_control("R", state):
        return RGB_check("R")


def GREEN_control(state):
    if RGB_control("G", state):
        return RGB_check("G")


def BLUE_control(state):
    if RGB_control("B", state):
        return RGB_check("B")


def main():
    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare({
        'Omega LED': {
            'type': 'bool',
            'value': False,
            'bind': omega_led
        },
        'RGB LED - Red': {
            'type': 'bool',
            'value': False,
            'bind': RED_control
        },
        'RGB LED - Green': {
            'type': 'bool',
            'value': False,
            'bind': GREEN_control
        },
        'RGB LED - Blue': {
            'type': 'bool',
            'value': False,
            'bind': BLUE_control
        }
    })
    device.declare_diag({
        'Host': gethostname(),
        'OS Name': " ".join(uname())
    })

    try:
        device.send_diag()
        while True:
            device.send_data()
            sleep(DATA_SENDING_INTERVAL)

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, exc_info()[0])

    finally:
        exit()


if __name__ == '__main__':
    main()
