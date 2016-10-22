#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from platform import platform

SUPPORTED_TYPE = 'cpu'
RPI_CPU_TEMPERATURE_CMD = "vcgencmd measure_temp"
CHIP_CPU_TEMPERATURE_CMD = "echo $(sudo i2cget -y -f 0 0x34 0x5e) $(sudo i2cget -y -f 0 0x34 0x5f)"

PLATFORM = platform.get()

class CpuTemperature(object):
    def __init__(self):
        self.type = SUPPORTED_TYPE

    def read(self):
        if PLATFORM == "CHIP":
            msb, lsb = subprocess.check_output(CHIP_CPU_TEMPERATURE_CMD, shell=True).split()
            cpu_temperature = (int(msb, 0) << 4 | int(lsb, 0) & 15) / 10 - 144.7
        elif PLATFORM == "RPI":
            cpu_temperature = float(subprocess.check_output(RPI_CPU_TEMPERATURE_CMD, shell=True) \
                .lstrip("temp=").rstrip("'C\n"))
        return round(cpu_temperature, 2)
