#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

W1_DEVICES = '/sys/bus/w1/devices/'
W1_SENSOR_PATTERN = re.compile('(10|22|28)-.+', re.IGNORECASE)


def sensor_full_path(sensor):
    return os.path.join(W1_DEVICES, sensor, 'w1_slave')


def find_all():
    return [x for x in os.listdir(W1_DEVICES)
            if W1_SENSOR_PATTERN.match(x) and os.path.isfile(sensor_full_path(x))]
