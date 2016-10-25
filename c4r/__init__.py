# -*- coding: utf-8 -*-

from ds18b20 import DS18b20
from cpu_temperature import CpuTemperature
from net import IPAddress, Hostname

import os
import subprocess


def modprobe(module):
    cmd = 'modprobe {0}'.format(module)
    ret = os.system(cmd)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd)
