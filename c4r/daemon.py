#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Daemon(object):
    def __init__(self):
        self.token = None
        self.bind_handlers = None

    def set_device_token(self, token):
        self.token = token

    def read_persistent(self, variable, handler):
        handler(variable)

    # def add_bind_handler(self, address, handler):
    #     pass
