#!/usr/bin/env python2.7

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Try sudo <your command>")
import sys
import time

import c4r

DeviceToken = '5655bba0160533c60e650bfd'


def CoolerControl(value):
    GPIO.output(17, value)
    return GPIO.input(17)


Variables = {
    'CurrentTemp': {
        'title': 'Temp sensor reading',
        'type': 'numeric',
        'bind': 'onewire',
        'address': ''  # first found
    },
    'SetTemp': {
        'title': 'Target temperature',
        'type': 'numeric',
        'value': 20
    },
    'CoolerOn': {
        'title': 'Cooler enabled',
        'type': 'bool',
        'value': False,
        'bind': CoolerControl
    }
}

HYST = 1


def main():
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(17, GPIO.OUT)

        while True:
            c4r.Process(Variables)  # reads values from persistent memory, sensors

            # Control routine - HYSTERESIS
            vars = Struct(Variables)
            if vars.CoolerOn.value:
                if vars.CurrTemp.value < vars.SetTemp.value:
                    vars.CoolerOn.Value = False
            else:
                if vars.CurrTemp.Value > vars.SetTemp.Value + HYST:
                    vars.CoolerOn.Value = True

            c4r.Process(Variables)  #writes values to GPIO
            c4r.SendReceive(Variables)  #reports and get new values from our site
            time.sleep(100)
    except:
        print "error", sys.exc_info()[0]
        raise
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
