#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Put your device token here. To get a device token, register at http://stage.cloud4rpi.io
DeviceToken = "YOUR_DEVICE_TOKEN"
LOG_FILE_PATH = '/var/log/cloud4rpi.log'
# LOG_FILE_PATH = 'log/cloud4rpi.log'

# Set the scan interval to best suit your needs
scanIntervalSeconds = 10

# Define the actuators settings here
Actuators = [
    {
        'name': 'LED on PIN 12',
        'address': 'LED',
        'parameters': [
            {'Mode': 'OUT'}
        ]
    }
]

# Define the variables here
Variables = [
    {
        'name': 'Temperature',
        'type': 'number',
        'value': 20
    }
]
