#!/usr/bin/env python2.7

import RPi.GPIO as GPIO


class ExampleScript(object):
    def __init__(self, config, conn):
        GPIO.setmode(GPIO.BOARD)

        self.conn = conn

        # TODO get rid of hardcode
        self.led_config = config['actuators'][0]
        self.id = self.led_config['_id']

        self.led_pin = 12
        self.button_pin = 16
        self.button_pin2 = 18

        self.led_state = False

        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # PUD_UP - ground on press.
        GPIO.setup(self.button_pin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # PUD_DOWN - 3.3V on press

        GPIO.output(self.led_pin, self.led_state)

    def run(self):
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING, callback=self.my_callback, bouncetime=300)
        while True:
            if self.conn.poll(1):
                self.on_new_state(self.conn.recv())

    def my_callback(self, channel):
        self.led_state = not self.led_state
        GPIO.output(self.led_pin, self.led_state)
        print 'Set LED state to {0} with BUTTON'.format(self.led_state)
        self.conn.send({'id': self.id, 'state': self.led_state})

    def on_new_state(self, data):
        if data['id'] != self.id:
            return

        new_state = False if data['state'] == 'false' else True
        if self.led_state == new_state:
            return
        self.led_state = new_state
        print 'Set LED state to {0} from WEB'.format(self.led_state)
        GPIO.output(self.led_pin, self.led_state)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print 'Cleanup.'
        GPIO.cleanup()
