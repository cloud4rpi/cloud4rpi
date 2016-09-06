#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

W1_DEVICES = '/sys/bus/w1/devices/'
W1_SENSOR_PATTERN = re.compile('(10|22|28)-.+', re.IGNORECASE)
SUPPORTED_TYPE = 'ds18b20'


def sensor_full_path(sensor):
    return os.path.join(W1_DEVICES, sensor, 'w1_slave')


def create_sensor_info(address):
    return {'address': address}


def find_all():
    return [create_sensor_info(x) for x in os.listdir(W1_DEVICES)
            if W1_SENSOR_PATTERN.match(x) and os.path.isfile(sensor_full_path(x))]


def read_whole_file(path):
    with open(path, 'r') as f:
        return f.read()


class DS18b20(object):
    @staticmethod
    def find_all():
        return [DS18b20(x['address']) for x in find_all()]

    def __init__(self, address):
        # TODO: W1_SENSOR_PATTERN.match(address) throw if invalid
        self.address = address
        self.type = SUPPORTED_TYPE

    def read(self):
        readings = read_whole_file(sensor_full_path(self.address))
        temp_token = 't='
        temp_index = readings.find(temp_token)
        if temp_index < 0:
            return None
        temp = readings[temp_index + len(temp_token):]
        return float(temp) / 1000
