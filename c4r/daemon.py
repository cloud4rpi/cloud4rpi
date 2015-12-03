#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time
from requests import RequestException
import signal

from multiprocessing import Pool
from c4r.log import Logger

# TODO remove or replace with c4r
import cloud4rpi.errors as errors
import c4r.helpers as helpers
import settings as settings

import c4r.ds18b20 as ds_sensor

log = Logger().get_log()

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

class Daemon(object):
    def __init__(self):
        self.pool = Pool(processes=4, initializer=init_worker)
        self.token = None
        self.me = None
        self.bind_handlers = {}

    def set_device_token(self, token):
        self.token = token

    @staticmethod
    def create_ds18b20_sensor(address):
        return {'type': 'ds18b20', 'address': address}

    @staticmethod
    def find_ds_sensors():
        return ds_sensor.find_all()
        # return [self.create_ds18b20_sensor(x) for x in addresses]

    def handler_exists(self, address):
        fn = self.bind_handlers.get(address)
        if fn is None:
            return False
        return hasattr(fn, '__call__')

    def address_exists(self, variable):
        config = variable['bind']
        return config['address']

    def register_variable_handler(self, address, handler):
        self.bind_handlers[address] = handler

    @staticmethod
    def read_persistent(variable, handler):
        handler(variable)

    def is_ds_sensor(self, variable):
        if ds_sensor.SUPPORTED_TYPE == helpers.get_variable_type(variable):
            return not helpers.get_variable_address(variable) is None
        return False

    def read_ds_sensor(self, variable):
        address = helpers.get_variable_address(variable)
        return ds_sensor.read(address)

    def read_persistence(self, variables):
        values = [self.read_ds_sensor(x) for x in variables if self.is_ds_sensor(x)]
        print values
        return values
        # [self.run_handler(x['address']) for x in variables if self.handler_exists(x['address'])]

    def run_handler(self, address):
        handler = self.bind_handlers[address]
        handler()

    def send_stream(self):
        ts = datetime.datetime.utcnow().isoformat()
        # TODO impl
        stream = {
            'ts': ts,
            'payload': {}
        }
        return helpers.post_stream(self.token, stream)

    def process_device_state(self, state):
        pass


    # def run(self):
    #     self.prepare()
    #     self.poll()
    #
    # def shutdown(self):
    #     print 'Terminate user scripts'
    #     self.pool.terminate()
    #     self.pool.join()
    #     print 'Done'
    #
    # def prepare(self):
    #     self.know_thyself()
    #     # TODO impl
    #
    # def know_thyself(self):
    #     log.info('Getting device configuration...')
    #     self.me = helpers.get_device(self.token)
    #     # TODO impl
    #
    # def poll(self):
    #     while True:
    #         self.tick()
    #         time.sleep(settings.scanIntervalSeconds)
    #
    # def tick(self):
    #     try:
    #         res = self.send_stream()
    #         self.process_device_state(res)
    #
    #     except RequestException, errors.ServerError:
    #         log.error('Failed. Skipping...')

