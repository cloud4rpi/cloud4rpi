# -*- coding: utf-8 -*-

import logging
from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler
import cloud4rpi.device
import cloud4rpi.mqtt_api
import cloud4rpi.config

from cloud4rpi.device import Device
from cloud4rpi.mqtt_api import MqttApi, connect_mqtt
from cloud4rpi.http_api import HttpApi
from cloud4rpi.errors import get_error_message

log = logging.getLogger(cloud4rpi.config.loggerName)
log.setLevel(logging.INFO)
log.addHandler(StreamHandler())


def set_logging_to_file(log_file_path):
    log_file = RotatingFileHandler(
        log_file_path,
        maxBytes=1024 * 1024,
        backupCount=10
    )
    log_file.setFormatter(Formatter('%(asctime)s: %(message)s'))
    log.addHandler(log_file)
