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
        self.button1_pin = 16
        self.button2_pin = 18

        self.led_state = False

        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setup(self.button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # PUD_UP - ground on press.
        GPIO.setup(self.button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # PUD_DOWN - 3.3V on press

        GPIO.output(self.led_pin, self.led_state)

    def run(self):
        GPIO.add_event_detect(self.button1_pin, GPIO.FALLING, callback=self.on_button1_pressed, bouncetime=300)
        GPIO.add_event_detect(self.button2_pin, GPIO.RISING, callback=self.on_button2_pressed, bouncetime=300)
        while True:
            if self.conn.poll(1):
                self.on_new_state(self.conn.recv())

    def on_button1_pressed(self, channel):
        self.led_state = not self.led_state
        print 'Set LED state to {0} with BUTTON'.format(self.led_state)
        GPIO.output(self.led_pin, self.led_state)
        self.conn.send({'id': self.id, 'state': 1 if self.led_state else 0})

    @staticmethod
    def on_button2_pressed(channel):
        print 'Button 2 pressed'

    def on_new_state(self, data):
        if data['id'] != self.id:
            return

        new_state = bool(data['state'])
        if self.led_state == new_state:
            return
        self.led_state = new_state
        print 'Set LED state to {0} from WEB'.format(self.led_state)
        GPIO.output(self.led_pin, self.led_state)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print 'Cleanup - {0} - {1} - {2}'.format(exc_type, exc_val, exc_tb)
        GPIO.cleanup()
