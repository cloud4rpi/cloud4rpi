#!/usr/bin/env python2.7

import sys
import time
import logging
from datetime import datetime, timedelta
import c4r  # Lib to send and receive commands
from c4r.platform import platform
from c4r.cpu_temperature import CpuTemperature
from c4r.ds18b20 import DS18b20

PLATFORM = platform.get()

try:
    if PLATFORM == "RPI":
        import RPi.GPIO as GPIO  # pylint: disable=F0401
    elif PLATFORM == "CHIP":
        import CHIP_IO.GPIO as GPIO
    gpio_loaded = True
except Exception as e:
    gpio_loaded = False
    print 'Warning! No RPi.GPIO loaded!'

# attempt load w1 modules
try:
    if PLATFORM == "RPI":
        c4r.modprobe('w1-gpio')
        c4r.modprobe('w1-therm')
    else:
        c4r.modprobe('w1_gpio')
        c4r.modprobe('w1_therm')
except:
    pass

# Put your device token here. To get a token, register at https://cloud4rpi.io
# ====================================
DEVICE_TOKEN = 'YOUR_DEVICE_TOKEN'
c4r.set_device_token(DEVICE_TOKEN)
# ====================================

# Constants
LED_PIN = 12
POLLING_INTERVAL_IN_SEC = 60
SENDING_INTERVAL_IN_SEC = 30
LOG_FILE_PATH = '/var/log/cloud4rpi.log'

# configure logging
c4r.set_logging_to_file(LOG_FILE_PATH)
c4r.set_logger_level(logging.INFO)
# c4r.set_logger_level(logging.DEBUG)  # uncomment to show debug messages
log = c4r.get_logger()

# detect the connected ds18b20 temperature sensors
ds_sensors = DS18b20.find_all()
log.info('Sensors found: ' + ','.join(['[ds18b20: {0}]'.format(x.address) for x in ds_sensors]))


# configure GPIO library
if gpio_loaded:
    if PLATFORM == "RPI": GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)


# handler for the button or switch variable
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    current = GPIO.input(LED_PIN)
    log.info('led_control handler - value changed from {0} to {1} '.format(value, current))
    return current


# Put variable declarations here
Variables = {
    # 'CurrentTemp_1': {
    #     'type': 'numeric',
    #     'bind': ds_sensors[0]
    # },

    # 'CurrentTemp_2': {
    #     'type': 'numeric',
    #     'bind': ds_sensors[1]
    # },
    #
    # 'LEDOn': {
    #     'type': 'bool',
    #     'value': False,
    #     'bind': led_control
    # },

    'CPUTemp': {
        'type': 'numeric',
        'bind': CpuTemperature()
    }
}


def main():
    log.info('App running...')

    c4r.connect_to_message_broker()
    c4r.register(Variables)  # Sends variable declarations to the server
    c4r.start_polling(POLLING_INTERVAL_IN_SEC)  # Sends variable declarations to the server

    # main loop
    try:
        next_sent = datetime.now()
        while True:
            if datetime.now() >= next_sent:
                # Reads bound values from the persistent memory and sensors
                c4r.read_variables(Variables)
                c4r.send(Variables)  # Sends variable values to the server
                next_sent = next_sent + timedelta(seconds=SENDING_INTERVAL_IN_SEC)

            time.sleep(1)

    except KeyboardInterrupt:
        log.info('Keyboard interrupt received. Stopping...')
        c4r.cleanup()
        sys.exit(0)

    except Exception as e:
        error = c4r.get_error_message(e)
        log.error("ERROR! {0} {1}".format(error, sys.exc_info()[0]))
        c4r.cleanup()
        raise


if __name__ == '__main__':
    main()
