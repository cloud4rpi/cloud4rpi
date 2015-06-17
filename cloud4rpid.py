#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import requests
import json
import time

from settings import DeviceToken

W1_DEVICES = '/sys/bus/w1/devices/'
W1_SENSOR_PATTERN = re.compile('(10|22|28)-.+', re.IGNORECASE)


def sensor_full_path(sensor):
    return os.path.join(W1_DEVICES, sensor)


def find_sensors():
    return [x for x in os.listdir(W1_DEVICES)
            if W1_SENSOR_PATTERN.match(x) and os.path.isdir(sensor_full_path(x))]


def read_sensor(address):
    readings = read_whole_file(os.path.join(W1_DEVICES, address, 'w1_slave'))
    temp_token = 't='
    temp_index = readings.find(temp_token)
    if temp_index < 0:
        return 0.0
    temp = readings[temp_index + len(temp_token):]
    return address, float(temp) / 1000


def read_whole_file(path):
    with open(path, 'r') as f:
        return f.read()


def read_sensors():
    return [read_sensor(x) for x in map(lambda x: x, find_sensors())]


# TODO: check status_code of the respose and throw exceptions where appropriate. IMPORTANT!

def get_device(token):
    res = requests.get('http://stage.cloud4rpi.io:3000/api/device/{0}/'.format(token))
    return ServerDevice(res.json())


def put_device(token, device):
    res = requests.put('http://stage.cloud4rpi.io:3000/api/device/{0}/'.format(token),
                       headers={'api_key': token},
                       data=device.dump())
    return ServerDevice(res.json())


def post_stream(token, stream):
    res = requests.post('http://stage.cloud4rpi.io:3000/api/device/{0}/stream/'.format(token),
                        headers={'api_key': token},
                        data=json.dumps(stream))
    return res.json()


class ServerDevice:
    def __init__(self, device_json):
        self.json = device_json
        self.addresses = None
        self.__extract_addresses()

    def sensor_addrs(self):
        return self.addresses

    def add_sensors(self, sensors):
        self.json['sensors'] += map(lambda x: {'address': x}, sensors)
        self.__extract_addresses()

    def whats_new(self, sensors):
        existing = self.sensor_addrs()
        return set(sensors) - set(existing)

    def dump(self):
        return json.dumps(self.json)

    def map_sensors(self, readings):
        # FIXME: Add checks on key presence in index
        index = {sensor['address']: sensor['_id'] for sensor in self.json.get('sensors')}
        return [{index[address]: reading} for address, reading in readings]

    def __extract_addresses(self):
        self.addresses = [sensor['address'] for sensor in self.json['sensors']]


class RpiDaemon:
    def __init__(self):
        self.sensors = None
        self.me = None
        self.token = DeviceToken

    def run(self):
        print 'Running...'

        self.prepare_sensors()
        self.poll()

    def prepare_sensors(self):
        self.know_thyself()
        self.find_sensors()
        self.register_new_sensors()  # if any

    def know_thyself(self):
        self.me = get_device(self.token)

    def find_sensors(self):
        self.sensors = find_sensors()

    def register_new_sensors(self):
        new_sensors = self.me.whats_new(self.sensors)
        if len(new_sensors) > 0:
            self.me.add_sensors(new_sensors)
            self.me = put_device(self.token, self.me)

    def poll(self):
        # TODO:
        # run an infinite loop with sleep
        # catch exceptions, break the on unauth exceptions
        pass

    def tick(self):
        ts = int(time.time())
        readings = read_sensors()
        payload = self.me.map_sensors(readings)
        stream = {
            'ts': ts,
            'payload': payload
        }
        post_stream(self.token, stream)


if __name__ == "__main__":
    daemon = RpiDaemon()
    daemon.run()
