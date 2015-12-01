#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ds18b20 import find_all


class Daemon(object):

    def __init__(self):
        self.token = None
        self.bind_handlers = {}

    def set_device_token(self, token):
        self.token = token

    def find_ds_sensors(self):
        sensors = find_all()
        return sensors

    def register_variable_handler(self, address, handler):
        self.bind_handlers[address] = handler

    def read_persistent(self, variable, handler):
        handler(variable)

    # def add_bind_handler(self, address, handler):
    #     pass
