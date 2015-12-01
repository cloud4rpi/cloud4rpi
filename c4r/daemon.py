#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ds18b20 import find_all


class Daemon(object):
    def __init__(self):
        self.token = None
        self.bind_handlers = {}

    def set_device_token(self, token):
        self.token = token

    def create_ds18b20_sensor(self, address):
        return {'type': 'ds18b20', 'address': address}

    def find_ds_sensors(self):
        addresses = find_all()
        return map(self.create_ds18b20_sensor, addresses)

    def handler_exists(self, address):
        fn = self.bind_handlers.get(address)
        if fn is None:
            return False
        return hasattr(fn, '__call__')

    def register_variable_handler(self, address, handler):
        self.bind_handlers[address] = handler

    def read_persistent(self, variable, handler):
        handler(variable)

    def process_variables(self, variables):
        [self.run_handler(x['address']) for x in variables if self.handler_exists(x['address'])]

    def run_handler(self, address):
        handler = self.bind_handlers[address]
        handler()

