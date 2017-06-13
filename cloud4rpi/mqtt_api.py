# -*- coding: utf-8 -*-

import time
import logging
import json

from cloud4rpi import config
from cloud4rpi import utils
from cloud4rpi.errors import MqttConnectionError

import paho.mqtt.client as mqtt

KEEP_ALIVE_INTERVAL = 60 * 10
MQTT_ERR_SUCCESS = 0

log = logging.getLogger(config.loggerName)


def connect_mqtt(device_token):
    api = MqttApi(device_token)
    __attempt_to_connect_with_retries(api)
    return api


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


class MqttApi(object):
    def __init__(self,
                 device_token,
                 host=config.mqqtBrokerHost,
                 port=config.mqttBrokerPort):
        utils.guard_against_invalid_token(device_token)

        def noop_on_command(cmd):
            pass

        self.__device_token = device_token
        self.__client = mqtt.Client(device_token, clean_session=False)
        self.__host = host
        self.__port = port

        self.on_command = noop_on_command

    def __format_topic(self, tail):
        return 'devices/{0}/{1}'.format(self.__device_token, tail)

    def connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc != MQTT_ERR_SUCCESS:
                log.error('Connection failed: %s', rc)
                raise MqttConnectionError(rc)
            topic = self.__format_topic('commands')
            log.debug('Listen for %s', topic)
            self.__client.subscribe(topic, qos=1)

        def on_message(client, userdata, msg):
            log.info('Command received %s: %s', msg.topic, msg.payload)
            if callable(self.on_command):
                payload = msg.payload.decode() \
                    if isinstance(msg.payload, bytes) else msg.payload
                self.on_command(json.loads(payload))

        def on_disconnect(client, userdata, rc):
            log.info('MQTT disconnected with code: %s', rc)
            self.__on_disconnect(rc)

        self.__client.on_connect = on_connect
        self.__client.on_message = on_message
        self.__client.on_disconnect = on_disconnect

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
                log.info('Reconnection failed: %s', str(e))
                time.sleep(retry_interval)

    def disconnect(self):
        self.__client.loop_stop()
        self.__client.disconnect()

    def publish_config(self, cfg):
        self.__publish(self.__format_topic('config'), cfg)

    def publish_data(self, data):
        self.__publish(self.__format_topic('data'), data)

    def publish_diag(self, diag):
        self.__publish(self.__format_topic('diagnostics'), diag)

    def __publish(self, topic, payload=None):
        if payload is None:
            return
        msg = {
            'ts': utils.utcnow(),
            'payload': payload,
        }
        log.info('Publishing %s: %s', topic, msg)
        self.__client.publish(topic, payload=json.dumps(msg))