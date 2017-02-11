# -*- coding: utf-8 -*-

import cloud4rpi
from os import uname
from socket import gethostname
from sys import exit, exc_info
from time import sleep
from subprocess import call, check_output


DATA_SENDING_INTERVAL = 30  # secs


# find the path to the Omega LED
led_name = check_output(["uci", "get", "system.@led[0].sysfs"])
led_brightness_path = "/sys/class/leds/%s/brightness" % (led_name.rstrip())

def omega_led_brightness(brightness):
    open(led_brightness_path, 'w').write('1' if brightness else '0')
    return bool(int(open(led_brightness_path, 'r').read()))

# Should work but does not :(
# import onionGpio
# RGB_R = onionGpio.OnionGpio(17)
# RGB_G = onionGpio.OnionGpio(16)
# RGB_B = onionGpio.OnionGpio(15)
# map(lambda g: g.setOutputDirection(), [RGB_R, RGB_G, RGB_B])
# RGB_B.setValue(True)

RGB = {'R': '17', 'G': '16', 'B': '15'}  # Expansion board

for pin in RGB.itervalues():
    call("gpioctl dirout-high " + pin, shell=True)

def RGB_control(led, value):
    operation = 'clear' if value else 'set'  # (sic)
    try:
        return not call("gpioctl %s %s" % (operation, RGB[led]), shell=True)
    except:
        return False

def RGB_check(led):
    return 'LOW' in check_output(["gpioctl", "get", RGB[led]])

def RED_control(val):
    if RGB_control("R", val):
        return RGB_check("R")
    
def GREEN_control(val):
    if RGB_control("G", val):
        return RGB_check("G")
        
def BLUE_control(val):
    if RGB_control("B", val):
        return RGB_check("B")
        
def main():
    device = cloud4rpi.connect_mqtt('884hB8jz1x71JWRQPWf88XaUM')
    device.declare({
        'Omega LED':{
            'type': 'bool',
            'value': False,
            'bind': omega_led_brightness
        },
        'RGB LED - Red':{
            'type': 'bool',
            'value': False,
            'bind': RED_control
        },
        'RGB LED - Green':{
            'type': 'bool',
            'value': False,
            'bind': GREEN_control
        },
        'RGB LED - Blue':{
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
        exit(0)
    

if __name__ == '__main__':
    main()