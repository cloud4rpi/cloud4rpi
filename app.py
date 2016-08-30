#!/usr/bin/env python2.7

import sys
import time
import c4r  # Lib to send and receive commands

try:
    import RPi.GPIO as GPIO  # pylint: disable=F0401

    gpio_loaded = True
except Exception as e:
    print 'Warning! No RPi.GPIO loaded!'
    gpio_loaded = False

# load w1 modules
c4r.modprobe('w1-gpio')
c4r.modprobe('w1-therm')


# Put your device token here. To get a token, register at https://cloud4rpi.io
DEVICE_TOKEN = 'YOUR_DEVICE_TOKEN'
c4r.set_device_token(DEVICE_TOKEN)

# object to provide cpu temperature
cpu_temp = c4r.find_cpu()

# detect connected ds18b20 temp sensors
ds_sensors = c4r.find_ds_sensors()
print 'SENSORS FOUND ', ds_sensors


def bind_sensor(sensors, index):
    if sensors is not None and len(sensors) > index:
        return sensors[index]
    return None

# Constants
DS_SENSOR_1_INDEX = 0
DS_SENSOR_2_INDEX = 1
LED_PIN = 12
POOLING_INTERVAL_IN_SEC = 60

# configure GPIO library
if gpio_loaded:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)


# button or switch variable handler
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    return GPIO.input(LED_PIN)


# Put required variable declaration here
Variables = {
    # 'CurrentTemp_1': {
    #     'type': 'numeric',
    #     'bind': bind_sensor(ds_sensors, DS_SENSOR_1_INDEX)
    # },
    #
    # 'CurrentTemp_2': {
    #     'type': 'numeric',
    #     'bind': bind_sensor(ds_sensors, DS_SENSOR_2_INDEX)
    # },
    #
    # 'LEDOn': {
    #     'type': 'bool',
    #     'value': False,
    #     'bind': led_control
    # },

    'CPU': {
        'type': 'numeric',
        'bind': cpu_temp
    }
}

def main():

    c4r.start_message_broker_listen()  # Receives control commands from server
    c4r.register(Variables)  # Sends variable declarations to server
    c4r.start_polling(POOLING_INTERVAL_IN_SEC)  # Sends system diagnostic data to server

    # main loop
    try:
        while True:
            c4r.read_variables(Variables)  # Reads bounded values from persistent memory, sensors
            c4r.send_receive(Variables)  # Sends variable values data to server

            time.sleep(10)

    except KeyboardInterrupt:
        print 'Keyboard interrupt received. Stopping...'
        c4r.finalize()
        sys.exit(0)

    except Exception as e:
        error = c4r.get_error_message(e)
        print "error", error, sys.exc_info()[0]
        c4r.finalize()
        raise


if __name__ == '__main__':
    main()
