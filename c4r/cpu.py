#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

SUPPORTED_TYPE = 'cpu'
CPU_TEMPERATURE_CMD = "vcgencmd measure_temp"

class Cpu(object):
    def __init__(self):
        self.type = SUPPORTED_TYPE
        self._temperature = None

    def read(self):
        cpu_temperature_str = subprocess.check_output(CPU_TEMPERATURE_CMD, shell=True) \
            .lstrip("temp=").rstrip("'C\n")
        self._temperature = float(cpu_temperature_str)

    def get_temperature(self):
        return self._temperature
