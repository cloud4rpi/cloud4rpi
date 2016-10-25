# -*- coding: utf-8 -*-

from c4r.ds18b20 import DS18b20
from c4r.cpu_temperature import CpuTemperature
from c4r.net import IPAddress, Hostname
from c4r.mqtt_client import InvalidTokenError
from subprocess import CalledProcessError

import os
import subprocess
import logging
import logging.handlers
import c4r.device
import c4r.mqtt_client
import c4r.config


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


def create_logger():
    logger = logging.getLogger(c4r.config.loggerName)
    logger.setLevel(logging.INFO)
    set_logging_to_console(logger)


def set_logging_to_console(logger):
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console)


def set_logging_to_file(logger, log_file_path):
    file = logging.handlers.RotatingFileHandler(log_file_path,
                                                maxBytes=1024 * 1024,
                                                backupCount=10)
    file.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(file)


create_logger()
