#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

CPU_TEMPERATURE_CMD = "vcgencmd measure_temp"
#CPU_USAGE_CMD = "top -n2 -d.1 | awk -F ',' '/Cpu\(s\):/ {print $1}'"
#ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')

def read():
    cpu_temperature_str = subprocess.check_output(CPU_TEMPERATURE_CMD, shell=True) \
        .lstrip("temp=").rstrip("'C\n")

    cpu_temperature = float(cpu_temperature_str)
    return cpu_temperature

# def get_cpu_usage():
#     cpu_usage_str = subprocess.check_output(CPU_USAGE_CMD, shell=True).splitlines()[-1]
#     stripped = strip_escape_codes(cpu_usage_str)
#     return extract_usage(stripped)

# def strip_escape_codes(s):
#     return ANSI_ESCAPE.sub('', s)

# def extract_usage(s):
#     return float(s.lstrip('%Cpu(s): ').rstrip(' us'))
