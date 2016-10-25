# -*- coding: utf-8 -*-

from cloud4rpi.ds18b20 import DS18b20
from cloud4rpi.cpu_temperature import CpuTemperature
from cloud4rpi.net import IPAddress, Hostname
from cloud4rpi.api_client import InvalidTokenError
from subprocess import CalledProcessError

import os
import subprocess
import logging
import logging.handlers
import cloud4rpi.device
import cloud4rpi.api_client
import cloud4rpi.config


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
    api = cloud4rpi.api_client.MqttApi(device_token)
    api.connect()
    return cloud4rpi.device.Device(api)


def create_logger():
    logger = logging.getLogger(cloud4rpi.config.loggerName)
    logger.setLevel(logging.INFO)
    set_logging_to_console(logger)


def set_logging_to_console(logger):
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console)


def set_logging_to_file(logger, log_file_path):
    log_file = logging.handlers.RotatingFileHandler(log_file_path,
                                                    maxBytes=1024 * 1024,
                                                    backupCount=10)
    log_file.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(log_file)


create_logger()
