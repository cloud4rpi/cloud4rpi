#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
from c4r.logger import get_logger
from c4r import helpers
import c4r.ds18b20 as ds_sensor
from c4r import cpu
from c4r import transport
from c4r import mqtt_listener
import c4r
import json

device_token = None
reg_vars = None
log = get_logger()


def set_device_token(token):
    global device_token  # pylint: disable=W0603
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


def is_cpu(variable):
    return helpers.bind_is_instance_of(variable, cpu.Cpu)


def read_ds_sensor(variable):
    address = helpers.get_variable_address(variable)
    if address is not None:
        variable['value'] = ds_sensor.read(address)


def read_system(variables):
    [read_cpu(x) for x in variables.itervalues() if is_cpu(x)]


def read_cpu(variable):
    if helpers.bind_is_instance_of(variable, cpu.Cpu):
        c = helpers.get_variable_bind(variable)
        c.read()
        variable['value'] = c.get_temperature()


def read_persistent(variables):
    values = [read_ds_sensor(x) for x in variables.itervalues() if is_ds_sensor(x)]
    return values


def collect_readings(variables):
    readings = {name: helpers.get_variable_value(value) for name, value in variables.iteritems()}
    return readings


def send_receive(variables):
    readings = collect_readings(variables)
    return send_stream(readings)


def send_stream(stream):
    transport = get_active_transport()
    return transport.send_stream(device_token, stream)


def get_active_transport():
    return transport.MqttTransport()


def broker_message_handler(msg):
    if reg_vars is None:
        print 'No variables registered. Skipping.'
        return
    print 'Handle message:', msg
    new_values = json.loads(msg)
    for var_name, value in new_values.iteritems():
        bind = helpers.get_variable_bind(reg_vars[var_name])
        if helpers.bind_is_handler(bind):
            result = run_bind_method(var_name, bind, value)
            reg_vars[var_name]['value'] = bool(result) if reg_vars[var_name]['type'] == 'bool' else result


def register(variables):
    global reg_vars
    variables_decl = [{'name': name, 'type': value['type']}
                      for name, value in variables.iteritems()]
    config = {'variables': variables_decl}

    reg_vars = variables
    c4r.on_broker_message += broker_message_handler

    log.info('Sending device configuration...')
    transport = get_active_transport()
    return transport.send_config(device_token, config)


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


def process_event(variables, payload):
    for name, props in variables.iteritems():
        bind = helpers.get_variable_bind(props)
        if helpers.bind_is_handler(bind):
            val = helpers.get_by_key(payload, name)
            run_bind_method(name, bind, val)


def process_variables(variables, server_msg):
    events = helpers.extract_server_events(server_msg)
    payloads = helpers.extract_all_payloads(events)
    for x in payloads:
        process_event(variables, x)


def start_mqtt_listen():
    mqtt_listener.start_listen(device_token)


def stop_mqtt_listen():
    mqtt_listener.stop_listen()
