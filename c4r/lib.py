#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Pool

import datetime
import signal
from c4r.logger import get_logger
from c4r import helpers
import c4r.ds18b20 as ds_sensor
from c4r import cpu

device_token = None

log = get_logger()


def set_device_token(token):
    global device_token # pylint: disable=W0603
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
    if  helpers.bind_is_instance_of(variable, cpu.Cpu):
        return True
    return ds_sensor.SUPPORTED_TYPE == helpers.get_variable_type(variable)


def read_ds_sensor(variable):
    address = helpers.get_variable_address(variable)
    if not address is None:
        variable['value'] = ds_sensor.read(address)


def read_cpu(variable):
    if helpers.bind_is_instance_of(variable, cpu.Cpu):
        c = helpers.get_variable_bind(variable)
        c.read()
        variable['value'] = c.get_temperature()
        print 'Done!'


def read_persistent(variables):
    values = [read_ds_sensor(x) for x in variables.itervalues() if is_ds_sensor(x)]
    return values


def collect_readings(variables):
    readings = {name: helpers.get_variable_value(value) for name, value in variables.iteritems() \
                if is_out_variable(value)}
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


def register(variables):
    variables_decl = [{'name': name, 'title': value['title'], 'type': value['type']}
                      for name, value in variables.iteritems()]
    return helpers.put_device_variables(device_token, variables_decl)


def run_handler(self, address):
    handler = self.bind_handlers[address]
    handler()


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def run_bind_method(var_name, method, current_value):
    print 'Call bind method for {0} variable...'.format(var_name)
    result = method(current_value)
    print 'Done bind method for {0} variable... Result: {1}'.format(var_name, result)

    return result


pool = Pool(processes=1, initializer=init_worker)


def process_variables(variables, payloads):
    for name, props in variables.iteritems():
        if helpers.bind_is_instance_of(props, cpu.Cpu):
            continue

        bind = helpers.get_variable_bind(props)
        if helpers.bind_is_handler(bind):
            pool.apply_async(run_bind_method, args=(name, bind, helpers.get_payload_value(name, payloads)))
