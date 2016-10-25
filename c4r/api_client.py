from datetime import datetime
from c4r import config

import re
import json
import paho.mqtt.client as mqtt


def guard_against_invalid_token(token):
    token_re = re.compile('[1-9a-km-zA-HJ-NP-Z]{23,}')
    if not token_re.match(token):
        raise InvalidTokenError('Invalid device token')


class InvalidTokenError(Exception):
    pass


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
        # TODO: clean_session=False
        self.__client = mqtt.Client(client_id)
        self.__host = host
        self.__port = port
        self.__msg_topic = 'iot-hub/messages/{0}'.format(device_token)
        self.__cmd_topic = 'iot-hub/commands/{0}'.format(device_token)
        self.__username = username
        self.__password = password
        self.on_command = noop_on_command

    def connect(self):
        def on_message(client, userdata, message):
            if hasattr(self, 'on_command') and callable(self.on_command):
                self.on_command(json.loads(message.payload))

        def on_connect(*args):
            self.__client.subscribe(self.__cmd_topic)

        self.__client.on_connect = on_connect
        self.__client.on_message = on_message
        # TODO: on_disconnect
        self.__client.username_pw_set(self.__username, self.__password)
        # TODO: keepalive=KEEP_ALIVE_INTERVAL
        self.__client.connect(self.__host, port=self.__port)
        self.__client.loop_start()

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
        self.__client.publish(self.__msg_topic, payload=json.dumps(msg))
