#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

SUPPORTED_TYPE = 'cpu'
CPU_TEMPERATURE_CMD = "vcgencmd measure_temp"


class CpuTemperature(object):
    def __init__(self):
        self.type = SUPPORTED_TYPE

    def read(self):
        cpu_temperature_str = subprocess.check_output(CPU_TEMPERATURE_CMD, shell=True) \
            .lstrip("temp=").rstrip("'C\n")
        return float(cpu_temperature_str)
