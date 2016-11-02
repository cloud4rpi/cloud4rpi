# -*- coding: utf-8 -*-

import time
import logging
import re
import json

from datetime import datetime
from cloud4rpi import config

import paho.mqtt.client as mqtt

KEEP_ALIVE_INTERVAL = 60 * 10
MQTT_ERR_SUCCESS = 0

log = logging.getLogger(config.loggerName)


def guard_against_invalid_token(token):
    token_re = re.compile('[1-9a-km-zA-HJ-NP-Z]{23,}')
    if not token_re.match(token):
        raise InvalidTokenError(token)


class InvalidTokenError(Exception):
    pass


class MqttConnectionError(Exception):
    def __init__(self, code):
        super(MqttConnectionError, self).__init__()
        self.code = code


class MqttApi(object):
    def __init__(self,
                 device_token,
                 username=config.mqqtBrokerUsername,
                 password=config.mqttBrokerPassword,
                 host=config.mqqtBrokerHost,
                 port=config.mqttBrokerPort):
        guard_against_invalid_token(device_token)

        def noop_on_command(cmd):
            pass

        client_id = 'c4r-{0}'.format(device_token)
        self.__client = mqtt.Client(client_id, clean_session=False)
        self.__host = host
        self.__port = port
        self.__msg_topic = 'iot-hub/messages/{0}'.format(device_token)
        self.__cmd_topic = 'iot-hub/commands/{0}'.format(device_token)
        self.__username = username
        self.__password = password
        self.on_command = noop_on_command

    def connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc != MQTT_ERR_SUCCESS:
                log.error('Connection failed: %s', rc)
                raise MqttConnectionError(rc)
            log.debug('Listen for %s', self.__cmd_topic)
            self.__client.subscribe(self.__cmd_topic, qos=1)

        def on_message(client, userdata, msg):
            log.info('Command received %s: %s', msg.topic, msg.payload)
            if callable(self.on_command):
                self.on_command(json.loads(msg.payload))

        def on_disconnect(client, userdata, rc):
            log.info('MQTT disconnected with code: %s', rc)
            self.__on_disconnect(rc)

        self.__client.on_connect = on_connect
        self.__client.on_message = on_message
        self.__client.on_disconnect = on_disconnect
        self.__client.username_pw_set(self.__username, self.__password)
        log.info('MQTT connecting %s:%s', config.mqqtBrokerHost,
                 config.mqttBrokerPort)
        self.__client.connect(self.__host, self.__port,
                              keepalive=KEEP_ALIVE_INTERVAL)
        self.__client.loop_start()

    def __on_disconnect(self, rc):
        if rc == MQTT_ERR_SUCCESS:
            return

        attempts = 0
        retry_interval = 1
        while True:
            attempts += 1
            log.info('Attempting to reconnect... %s', attempts)
            try:
                self.__client.reconnect()
                log.info("Reconnected!")
                return
            except Exception as e:
                log.info('Reconnection failed: %s', e.message)
                time.sleep(retry_interval)

    def disconnect(self):
        self.__client.loop_stop()
        self.__client.disconnect()

    def publish_config(self, cfg):
        self.__publish('config', cfg)

    def publish_data(self, data):
        self.__publish('data', data)

    def publish_diag(self, diag):
        self.__publish('system', diag)

    def __publish(self, msg_type, payload):
        msg = {
            'type': msg_type,
            'ts': datetime.utcnow().isoformat(),
            'payload': payload,
        }
        log.info('Publishing %s: %s', self.__msg_topic, msg)
        self.__client.publish(self.__msg_topic, payload=json.dumps(msg))
