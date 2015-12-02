#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ds18b20
from log import Logger
import daemon

log = Logger().get_log()
dmn = daemon.Daemon()

def find_ds_sensors():
    return ds18b20.find_all()

def set_device_token(token):
    dmn.set_device_token(token)

def process_variables(vars):
    dmn.process_variables(vars)

def process_variables(vars):
    dmn.process_variables(vars)
