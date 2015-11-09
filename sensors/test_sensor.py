#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random

W1_DEVICES = '/sys/bus/w1/devices/'


def sensor_full_path(sensor):
    return os.path.join(W1_DEVICES, sensor, 'w1_slave')


def find_all():
    return [u'28-000000000000']


def read(address):
    temp = random.uniform(20.0, 25.0)
    return address, temp
