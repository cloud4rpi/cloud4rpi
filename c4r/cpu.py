#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

SUPPORTED_TYPE = 'cpu'

CPU_TEMPERATURE_CMD = "vcgencmd measure_temp"

def read():
    cpu_temperature_str = subprocess.check_output(CPU_TEMPERATURE_CMD, shell=True) \
        .lstrip("temp=").rstrip("'C\n")

    cpu_temperature = float(cpu_temperature_str)
    return cpu_temperature

