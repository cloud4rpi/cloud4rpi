# -*- coding: utf-8 -*-

from cloud4rpi.ds18b20 import DS18b20
from cloud4rpi.cpu_temperature import CpuTemperature
from cloud4rpi.net import IPAddress, Hostname

import time
import os
import subprocess
import logging
import logging.handlers
import cloud4rpi.device
import cloud4rpi.api_client
import cloud4rpi.config

log = logging.getLogger(cloud4rpi.config.loggerName)


def modprobe(module):
    cmd = 'modprobe {0}'.format(module)
    ret = os.system(cmd)
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd)


__messages = {
    KeyboardInterrupt: 'Interrupted',
    subprocess.CalledProcessError: 'Try run with sudo',
    cloud4rpi.api_client.InvalidTokenError:
        'Device token {0} is invalid. Please verify it.',
}


def get_error_message(e):
    return __messages.get(type(e), 'Unexpected error: {0}').format(e.message)


def connect_mqtt(device_token):
    api = cloud4rpi.api_client.MqttApi(device_token)
    __attempt_to_connect_with_retries(api)
    return cloud4rpi.device.Device(api)


def __attempt_to_connect_with_retries(api, attempts=10):
    retry_interval = 5
    for attempt in range(attempts):
        try:
            api.connect()
        except Exception as e:
            log.debug('MQTT connection error %s. Attempt %s', e, attempt)
            time.sleep(retry_interval)
            continue
        else:
            break
    else:
        msg = 'Impossible to connect to MQTT broker. Quiting.'
        log.error(msg)
        raise Exception(msg)


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
