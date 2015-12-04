#!/usr/bin/env python
# -*- coding: utf-8 -*-

from c4r import ds18b20
from c4r import lib
from c4r import error_messages


def get_error_message(e):
    return error_messages.get_error_message(e)


def find_ds_sensors():
    return ds18b20.find_all()


def set_device_token(token):
    lib.set_device_token(token)


def read_persistent(variables):
    lib.read_persistent(variables)


def process_variables(variables):
    lib.process_variables(variables)


def send_receive(variables):
    lib.send_receive(variables)
