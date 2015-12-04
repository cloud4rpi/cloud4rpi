#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from c4r.logger import get_logger
from c4r import helpers
import c4r.ds18b20 as ds_sensor

device_token = None

log = get_logger()

def set_device_token(token):
    global device_token
    device_token = token


def create_ds18b20_sensor(address):
    return {'type': 'ds18b20', 'address': address}


def find_ds_sensors():
    return ds_sensor.find_all()


def bind_handler_exists(variable):
    bind = helpers.get_variable_bind(variable)
    return helpers.bind_is_handler(bind)


def is_ds_sensor(variable):
    if ds_sensor.SUPPORTED_TYPE == helpers.get_variable_type(variable):
        return not helpers.get_variable_address(variable) is None
    return False


def is_out_variable(variable):
    return ds_sensor.SUPPORTED_TYPE == helpers.get_variable_type(variable)


def read_ds_sensor(variable):
    address = helpers.get_variable_address(variable)
    if not address is None:
        variable['value'] = ds_sensor.read(address)


def read_persistent(variables):
    values = [read_ds_sensor(x) for x in variables.itervalues() if is_ds_sensor(x)]
    return values


def collect_readings(variables):
    readings = {name: helpers.get_variable_value(value) for name, value in variables.iteritems() if is_out_variable(value)}
    return readings


def send_receive(variables):
    readings = collect_readings(variables)
    return send_stream(readings)


def send_stream(payload):
    ts = datetime.datetime.utcnow().isoformat()
    stream = {
        'ts': ts,
        'payload': payload
    }
    return helpers.post_stream(device_token, stream)


def run_handler(self, address):
    handler = self.bind_handlers[address]
    handler()

