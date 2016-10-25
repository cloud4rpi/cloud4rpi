# -*- coding: utf-8 -*-

from c4r.ds18b20 import DS18b20
from c4r.cpu_temperature import CpuTemperature
from c4r.net import IPAddress, Hostname
from c4r.mqtt_client import InvalidTokenError
from subprocess import CalledProcessError

import os
import subprocess
import c4r.device
import c4r.mqtt_client


def modprobe(module):
    cmd = 'modprobe {0}'.format(module)
    ret = os.system(cmd)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd)


messages = {
    KeyboardInterrupt: 'Interrupted',
    CalledProcessError: 'Try run with sudo',
    InvalidTokenError: 'Device token {0} is invalid. Please verify it.',
}


def get_error_message(e):
    return messages.get(type(e), 'Unexpected error: {0}').format(e.message)


def connect_mqtt(device_token):
    api = c4r.mqtt_client.MqttApi(device_token)
    api.connect()
    device = c4r.device.Device(api)
    return device
