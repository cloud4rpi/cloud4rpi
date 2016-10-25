# -*- coding: utf-8 -*-

import subprocess

CPU_TEMPERATURE_CMD = "vcgencmd measure_temp"


class CpuTemperature(object):
    def read(self):
        temp_str = subprocess.check_output(CPU_TEMPERATURE_CMD, shell=True) \
            .lstrip("temp=") \
            .rstrip("'C\n")
        return float(temp_str)
