#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
from c4r.logger import get_logger
from c4r.cpu_temperature import CpuTemperature
from c4r import net
from c4r import helpers
from c4r import transport
from c4r import mqtt_listener
import c4r
import json

device_token = None
reg_vars = {}
log = get_logger()

cpuTemp = CpuTemperature()
netObj = net.NetworkInfo()
mqtt = transport.MqttTransport()


def set_device_token(token):
    global device_token  # pylint: disable=W0603
    device_token = token


def read_variables(variables):
    [read_sensor(x) for x in variables.itervalues()]


def read_sensor(variable):
    sensor_or_handler = variable.get('bind', None)
    if sensor_or_handler is None:
        return
    try:
        variable['value'] = sensor_or_handler.read()
    except AttributeError:
        pass


def send(variables):
    if len(variables) == 0:
        return
    readings = {name: variable.get('value') for name, variable in variables.iteritems()}
    return mqtt.send_stream(device_token, readings)


def collect_system_readings():
    netObj.read()
    return {'CPU Temperature': cpuTemp.read(),
            'IPAddress': netObj.addr,
            'Host': netObj.host}


def send_system_info():
    log.info('[x] Sending system information...')
    return mqtt.send_system_stream(device_token, collect_system_readings())


def register(variables):
    log.info('[x] Sending device configuration...')
    global reg_vars
    variables_decl = [{'name': name, 'type': value['type']}
                      for name, value in variables.iteritems()]

    reg_vars = variables
    c4r.on_broker_message += broker_message_handler
    return mqtt.send_config(device_token, variables_decl)


def run_handler(self, address):
    handler = self.bind_handlers[address]
    handler()


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def broker_message_handler(msg):
    log.info('Handle message: {0}'.format(msg))
    payload = json.loads(msg)
    for name, value in payload.iteritems():
        variable = reg_vars.get(name, {})
        sensor_or_handler = variable.get('bind', None)
        if sensor_or_handler is None:
            log.info('No variable with name {0} registered. Skipping.'.format(name))
            continue

        try:
            log.info('[x] Call bind method for {0} variable with {1}'.format(name, value))
            result = sensor_or_handler(value)
            helpers.set_bool_variable_value(variable, result)
            log.info('[x] Done bind method for {0} variable with result: {1}'.format(name, result))
        except TypeError:
            pass
        except Exception as e:
            log.error('Error processing {0} variable\' bind function: {1}'.format(name, e))


def start_mqtt_listen():
    mqtt_listener.start_listen(device_token)


def stop_mqtt_listen():
    mqtt_listener.stop_listen()
