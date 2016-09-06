#!/usr/bin/env python2.7

import sys
import time
import logging
import c4r  # Lib to send and receive commands
from c4r.cpu_temperature import CpuTemperature
from c4r.ds18b20 import DS18b20
try:
    import RPi.GPIO as GPIO  # pylint: disable=F0401
    gpio_loaded = True
except Exception as e:
    gpio_loaded = False
    print 'Warning! No RPi.GPIO loaded!'

# load w1 modules
c4r.modprobe('w1-gpio')
c4r.modprobe('w1-therm')

# Put your device token here. To get a token, register at https://cloud4rpi.io
# ====================================
DEVICE_TOKEN = 'YOUR_DEVICE_TOKEN'
c4r.set_device_token(DEVICE_TOKEN)
# ====================================

# Constants
LED_PIN = 12
POOLING_INTERVAL_IN_SEC = 60
SENDING_INTERVAL_IN_SEC = 30
LOG_FILE_PATH = '/var/log/cloud4rpi.log'

# configure logging
c4r.set_logging_to_file(LOG_FILE_PATH)
c4r.set_logger_level(logging.INFO)
# c4r.set_logger_level(logging.DEBUG)  # uncomment to show debug messages
log = c4r.get_logger()

# detect connected ds18b20 temp sensors
log.info('Sensors found:')
ds_sensors = DS18b20.find_all()
for x in ds_sensors:
    log.info("ds18b20 - {0}".format(x.address))

# configure GPIO library
if gpio_loaded:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)


# button or switch variable handler
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    current = GPIO.input(LED_PIN)
    log.info('led_control handler - value changed from {0} to {1} '.format(value, current))
    return current


# Put required variable declaration here
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
    c4r.start_message_broker_listen()  # Receives control commands from server
    c4r.register(Variables)  # Sends variable declarations to server
    c4r.start_polling(POOLING_INTERVAL_IN_SEC)  # Sends system diagnostic data to server

    # main loop
    try:
        while True:
            c4r.read_variables(Variables)  # Reads bounded values from persistent memory, sensors
            c4r.send(Variables)  # Sends variable values data to server

            time.sleep(SENDING_INTERVAL_IN_SEC)

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
