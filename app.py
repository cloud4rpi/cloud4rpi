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


# Put your device token here. To get a device token, register at http://cloud4rpi.io
DEVICE_TOKEN = 'YOUR_DEVICE_TOKEN'
c4r.set_device_token(DEVICE_TOKEN)

cpu = c4r.find_cpu()
ds_sensors = c4r.find_ds_sensors()
print 'SENSORS FOUND ', ds_sensors


def bind_sensor(sensors, index):
    if not sensors is None and len(sensors) > index:
        return sensors[index]
    return None


if gpio_loaded:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)


def led_control(value=None):
    GPIO.output(11, value)
    return GPIO.input(11)


# Put required variable declaration here
Variables = {
    # 'CurrentTemp_1': {
    #     'type': 'numeric',
    #     'bind': bind_sensor(ds_sensors, 0)
    # },
    #
    # 'CurrentTemp_2': {
    #     'type': 'numeric',
    #     'bind': bind_sensor(ds_sensors, 1)
    # },
    #
    # 'LEDOn': {
    #     'type': 'bool',
    #     'value': False,
    #     'bind': led_control
    # },

    'CPU': {
        'type': 'numeric',
        'bind': cpu
    }
}


def on_event(*args, **kwargs):
    print 'Handle message:', (args, kwargs)


c4r.on_broker_message += on_event


def main():
    c4r.start_message_broker_listen()
    c4r.register(Variables)  # Send variable declarations to server
    try:
        while True:
            c4r.read_persistent(Variables)  # Reads values from persistent memory, sensors
            c4r.read_system(Variables)  # Reads CPU temperature

            server_msg = c4r.send_receive(Variables)

            c4r.process_variables(Variables, server_msg)
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
