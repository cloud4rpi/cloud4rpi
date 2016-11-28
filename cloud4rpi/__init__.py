# -*- coding: utf-8 -*-

import time
import subprocess
import logging
import cloud4rpi.device
import cloud4rpi.api_client
import cloud4rpi.config


log = logging.getLogger(cloud4rpi.config.loggerName)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

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
        raise Exception('Impossible to connect to MQTT broker. Quiting.')


def set_logging_to_file(log_file_path):
    log_file = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=1024 * 1024,
        backupCount=10
    )
    log_file.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    log.addHandler(log_file)
