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
import cloud4rpi.helpers as helpers
import settings as settings


from c4r.ds18b20 import find_all

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

    def find_ds_sensors(self):
        addresses = find_all()
        return [self.create_ds18b20_sensor(x) for x in addresses]

    def handler_exists(self, address):
        fn = self.bind_handlers.get(address)
        if fn is None:
            return False
        return hasattr(fn, '__call__')

    def register_variable_handler(self, address, handler):
        self.bind_handlers[address] = handler

    @staticmethod
    def read_persistent(variable, handler):
        handler(variable)

    def process_variables(self, variables):
        [self.run_handler(x['address']) for x in variables if self.handler_exists(x['address'])]

    def run_handler(self, address):
        handler = self.bind_handlers[address]
        handler()

    def run(self):
        self.prepare()
        self.poll()

    def shutdown(self):
        print 'Terminate user scripts'
        self.pool.terminate()
        self.pool.join()
        print 'Done'

    def prepare(self):
        self.know_thyself()
        # TODO impl

    def know_thyself(self):
        log.info('Getting device configuration...')
        self.me = helpers.get_device(self.token)
        # TODO impl

    def poll(self):
        while True:
            self.tick()
            time.sleep(settings.scanIntervalSeconds)

    def tick(self):
        try:
            res = self.send_stream()
            self.process_device_state(res)
            # TODO impl
        except RequestException, errors.ServerError:
            log.error('Failed. Skipping...')

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

