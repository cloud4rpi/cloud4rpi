# -*- coding: utf-8 -*-

import time
import logging
import json
from math import floor
import requests
from cloud4rpi import utils
from cloud4rpi import config

log = logging.getLogger(config.loggerName)


HEADERS = {"Content-type": "application/json"}


def post_request(url, data, retry_interval=1):
    try:
        return requests.post(url, headers=HEADERS, data=json.dumps(data))
    except requests.exceptions.RequestException as e:
        log.error(str(e))
        time.sleep(retry_interval)
        log.info('Attempting to make POST request in %s sec',
                 floor(retry_interval))
        return post_request(url, data, min(retry_interval * 2, 100))


def get_request(url, retry_interval=1):
    try:
        return requests.get(url, headers=HEADERS)
    except requests.exceptions.RequestException as e:
        log.error(str(e))
        time.sleep(retry_interval)
        log.info('Attempting to make GET request in %s sec',
                 floor(retry_interval))
        return get_request(url, min(retry_interval * 2, 100))


class HttpApi(object):
    def __init__(self,
                 device_token,
                 base_api_url=config.baseApiUrl):
        utils.guard_against_invalid_token(device_token)

        self.__device_token = device_token
        self.__base_api_url = base_api_url

    def __format_url(self, suffix):
        return '{0}/devices/{1}{2}'.format(self.__base_api_url,
                                           self.__device_token,
                                           suffix)

    @staticmethod
    def __format_stream(payload):
        return {
            'ts': utils.utcnow(),
            'payload': payload
        }

    def publish_config(self, cfg):
        log.info('Sending config: %s', cfg)
        url = self.__format_url('/config')
        return post_request(url, cfg)

    def publish_data(self, data):
        log.info('Sending data: %s', data)
        url = self.__format_url('/data')
        return post_request(url, HttpApi.__format_stream(data))

    def publish_diag(self, diag):
        log.info('Sending diagnostics: %s', diag)

        url = self.__format_url('/diagnostics')
        return post_request(url, HttpApi.__format_stream(diag))

    def fetch_commands(self):
        log.info('Fetching latest commands')
        url = self.__format_url('/commands/latest')
        return get_request(url)
