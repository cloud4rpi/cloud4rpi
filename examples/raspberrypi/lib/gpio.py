import RPi.GPIO as GPIO  # pylint: disable=F0401


class GpioActuator(object):
    def __init__(self, pin_number):
        self.pin_number = pin_number
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_number, GPIO.OUT)

    def get(self):
        return GPIO.input(self.pin_number)

    def set(self, value):
        GPIO.output(self.pin_number, value)
        return self.get()
