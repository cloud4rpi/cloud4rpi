#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from c4r import ds18b20
from c4r import lib
from c4r import mqtt_client
from c4r import error_messages
from c4r.helpers import verify_token
from c4r.logger import get_logger

log = get_logger()


def api_wrapper(method, *args):
    try:
        return method(*args)
    except Exception as e:
        log.error('API error: {0}'.format(get_error_message(e)))
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


def read_variables(variables):
    api_wrapper(lib.read_variables, variables)


def send(variables):
    verify_token(lib.device_token)
    return api_wrapper(lib.send, variables)


def send_system_info():
    verify_token(lib.device_token)
    return api_wrapper(lib.send_system_info)


def connect_to_message_broker():
    verify_token(lib.device_token)
    for attempt in range(10):
        try:
            mqtt_client.connect()
        except Exception as e:
            log.debug('MQTT connection error {0}. Attempt {1}'.format(e, attempt))
            time.sleep(5)
            continue
        else:
            break
    else:
        msg = 'Impossible to connect to MQTT broker. Quiting.'
        log.error(msg)
        raise Exception(msg)
