#!/usr/bin/env python
# -*- coding: utf-8 -*-

from c4r import ds18b20
from c4r.log import Logger
from c4r import lib

log = Logger().get_log()
lib = lib.Daemon()

def find_ds_sensors():
    return ds18b20.find_all()

def set_device_token(token):
    lib.set_device_token(token)

def read_persistent(variables):
    lib.read_persistent(variables)

def process_variables(variables):
    lib.process_variables(variables)
