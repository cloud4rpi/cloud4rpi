#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import requests
import json
import time

from datetime import datetime
from settings import DeviceToken

import settings_vendor as config

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
    return [read_sensor(x) for x in find_sensors()]


def get_device(token):
    res = requests.get('{0}/device/{1}/'.format(config.baseApiUrl, token))
    ensure_authenticated(res)
    return ServerDevice(res.json())


def put_device(token, device):
    res = requests.put('{0}/device/{1}/'.format(config.baseApiUrl, token),
                       headers={'api_key': token},
                       data=device.dump())
    ensure_authenticated(res)
    return ServerDevice(res.json())


def post_stream(token, stream):
    print 'sending {0} at {1}'.format(stream['payload'], datetime.fromtimestamp(stream['ts']).isoformat())

    res = requests.post('{0}/device/{1}/stream/'.format(config.baseApiUrl, token),
                        headers={'api_key': token},
                        data=json.dumps(stream))
    ensure_authenticated(res)
    return res.json()


def ensure_authenticated(res):
    if res.status_code == 401:
        raise AuthenticationError


class AuthenticationError(Exception):
    pass


class ServerDevice:
    def __init__(self, device_json):
        self.json = device_json
        self.addresses = None
        self.__extract_addresses()

    def sensor_addrs(self):
        return self.addresses

    def add_sensors(self, sensors):
        self.json['sensors'] += map(lambda x: {'name': x, 'address': x}, sensors)
        self.__extract_addresses()

    def whats_new(self, sensors):
        existing = self.sensor_addrs()
        return set(sensors) - set(existing)

    def dump(self):
        return json.dumps(self.json)

    def map_sensors(self, readings):
        # TODO: Don't build index on each call
        index = {sensor['address']: sensor['_id'] for sensor in self.json['sensors']}
        return [{index[address]: reading} for address, reading in readings if address in index]

    def __extract_addresses(self):
        self.addresses = [sensor['address'] for sensor in self.json['sensors']]


class RpiDaemon:
    def __init__(self):
        self.sensors = None
        self.me = None
        self.token = DeviceToken

    def run(self):
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
        while True:
            self.tick()
            time.sleep(config.scanInterval)

    def tick(self):
        ts = int(time.time())
        readings = read_sensors()
        payload = self.me.map_sensors(readings)
        stream = {
            'ts': ts,
            'payload': payload
        }
        post_stream(self.token, stream)


def modprobe(module):
    ret = os.system('modprobe {0}'.format(module))
    if ret != 0:
        raise EnvironmentError


if __name__ == "__main__":
    try:
        modprobe('w1-gpio')
        modprobe('w1-therm')
    except EnvironmentError:
        print 'Try "sudo python cloud4rpi.py"'
        exit(1)
    except Exception as e:
        print 'Unexpected error: {0}'.format(e.message)
        print 'Terminating...'
        exit(1)

    print 'Starting...'
    daemon = RpiDaemon()
    try:
        daemon.run()
    except AuthenticationError:
        print 'Authentication failed. Check your device token.'
        print 'Terminating...'
        exit(1)
    except Exception as e:
        print 'Unexpected error: {0}'.format(e.message)
        print 'Terminating...'
        exit(1)
