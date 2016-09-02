#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from c4r import ds18b20
from c4r import cpu
from c4r import lib
from c4r import mqtt
from c4r import error_messages
from c4r.helpers import verify_token


def api_wrapper(method, *args):
    try:
        return method(*args)
    except Exception as e:
        print 'API error: {0}'.format(get_error_message(e))
        return None


def get_error_message(e):
    return error_messages.get_error_message(e)


def set_device_token(token):
    api_wrapper(lib.set_device_token, token)


def register(variables):
    verify_token(lib.device_token)
    api_wrapper(lib.register, variables)


def find_ds_sensors():
    return api_wrapper(ds18b20.find_all)


def find_cpu():
    return api_wrapper(cpu.Cpu)


def read_variables(variables):
    api_wrapper(lib.read_variables, variables)


def send_receive(variables):
    verify_token(lib.device_token)
    return api_wrapper(lib.send_receive, variables)


def send_system_info():
    verify_token(lib.device_token)
    return api_wrapper(lib.send_system_info)


def connect():
    verify_token(lib.device_token)
    for attempt in range(10):
        try:
            mqtt.connect()
        except Exception as e:
            print 'MQTT connection error {0}. Attempt {1}'.format(e, attempt)
            time.sleep(5)
            continue
        else:
            break
    else:
        msg = 'Impossible to connect to MQTT broker. Quiting.'
        print msg
        raise Exception(msg)


def start_message_broker_listen():
    verify_token(lib.device_token)
    return api_wrapper(lib.start_mqtt_listen)


def stop_message_broker_listen():
    verify_token(lib.device_token)
    return api_wrapper(lib.stop_mqtt_listen)
