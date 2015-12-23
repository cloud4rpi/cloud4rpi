#!/usr/bin/env python
# -*- coding: utf-8 -*-

from c4r import ds18b20
from c4r import lib
from c4r import error_messages
from c4r.helpers import verify_token


def get_error_message(e):
    return error_messages.get_error_message(e)


def set_device_token(token):
    lib.set_device_token(token)


def register(variables):
    verify_token(lib.device_token)
    lib.register(variables)


def find_ds_sensors():
    verify_token(lib.device_token)
    return ds18b20.find_all()


def read_persistent(variables):
    verify_token(lib.device_token)
    lib.read_persistent(variables)


def process_variables(variables, payloads):
    verify_token(lib.device_token)
    lib.process_variables(variables, payloads)


def send_receive(variables):
    verify_token(lib.device_token)
    return lib.send_receive(variables)
