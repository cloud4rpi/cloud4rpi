#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# =============================================================================
# To run this sample,
# 1. pip install cloud4rpi
# 2. python examples/simple_mqtt_messaging.py
# =============================================================================

# This needed to be able to import the cloud4rpi directory from examples
if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

from cloud4rpi import api_client


def main():
    # First of all obtain the _token_ for your device from the device page
    # and connect to the api.
    # The token looks something like "4GPZFMVuacadesU21dBw47zJi"
    # it is the key that allows the device to communicate with the cloud4rpi.
    device_token = '!!! put your device token here !!!'
    client = api_client.MqttApi(device_token)
    client.connect()

    # Next declare the device _variables_. A device variable is
    # a key/value pair of the variable name and its type.
    # Only the "numeric" & "bool" types are currently supported.
    # The name should be unique.
    variables = [
        {'name': 'Temperature', 'type': 'numeric'},
        {'name': 'Cooler', 'type': 'bool'},
        {'name': 'TheAnswer', 'type': 'numeric'},
    ]
    client.publish_config(variables)

    # After publishing the device config
    # you can start sending some useful data.
    # Data consists of key/value pairs of variable name and its value.
    data = {
        'Temperature': 36.6,
        'Cooler': True,
        'TheAnswer': 42
    }
    client.publish_data(data)

    # You don't have to send all the declared variable values at once,
    # you could send only variables you're interested in at the moment.
    data = {
        'Temperature': 25
    }
    client.publish_data(data)

    # You can also send some _diagnostic_ data. It has the same form as
    # the "useful" data except you don't have to declare any variables
    # beforehand.
    diag = {
        'IPAddress': '127.0.0.1',
        'Hostname': 'weather_station',
        'CPU Load': 99
    }
    client.publish_diag(diag)


if __name__ == '__main__':
    main()
