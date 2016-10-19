import json
import time
import token
from datetime import datetime

from c4r import config
from c4r import helpers
from c4r import events
from c4r.logger import get_logger
import paho.mqtt.client as mqtt

KEEP_ALIVE_INTERVAL = 60 * 10
MQTT_ERR_SUCCESS = 0

log = get_logger()
client = None
device_token = None


def start():
    log.debug('MqttClient - starting')
    connect()
    client.loop_start()


def stop():
    if client is not None:
        client.loop_stop(force=True)
        log.debug('MqttClient - listening stopped')


def listen():
    topic = helpers.format_subscription_topic(device_token)
    log.debug('Listen for [{0}]'.format(topic))
    client.subscribe(topic, qos=1)


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        log.error('Connection failed: {0}'.format(rc))
        raise Exception('Mqtt connection failed')
    listen()


def on_disconnect(client, userdata, rc):
    log.info('MQTT disconnected. Reason: {0}'.format(rc))
    if rc != MQTT_ERR_SUCCESS:
        n = 1
        while True:
            try:
                log.info('Attempting to reconnect... {0}'.format(n))
                n += 1
                client.reconnect()
                log.info("Connection restored!")
                return
            except Exception as e:
                log.info('Reconnect error: {0}'.format(e.message))
                time.sleep(1)


def on_message(client, userdata, message):
    log.info('[x] MQTT message received: [{0}] - [{1}]'.format(message.topic, message.payload))
    emit_event(message.payload)


def emit_event(payload):
    events.on_broker_message(payload)


def publish(topic, stream):
    payload = json.dumps(stream)
    log.info('Publish to MQTT {0}: {1}'.format(topic, payload))
    client.publish(topic, payload, 0, True)


def connect():
    global client
    global device_token
    device_token = token.get_device_token()
    client_id = helpers.format_mqtt_client_id(device_token)
    client = mqtt.Client(client_id=client_id, clean_session=False)
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    log.info('MQTT connecting to {0}:{1}'.format(config.mqqtBrokerHost, config.mqttBrokerPort))
    try:
        client.username_pw_set(config.mqqtBrokerUsername, config.mqttBrokerPassword)
        client.connect(config.mqqtBrokerHost, config.mqttBrokerPort, KEEP_ALIVE_INTERVAL)
        client.loop_start()
    except Exception as e:
        log.error('Connection failed: {0}'.format(e))
        raise e


def disconnect():
    global client
    if client is not None:
        client.loop_stop()
        client.disconnect()
        client = None


class MqttApi(object):
    def __init__(self,
                 device_token,
                 username='c4r-user',
                 password='c4r-password',
                 host='localhost',
                 port=1883):
        # guard args
        client_id = 'c4r-{0}'.format(device_token)
        self.__client = mqtt.Client(client_id)
        self.__host = host
        self.__port = port
        self.__msg_topic = 'iot-hub/messages/{0}'.format(device_token)

    def connect(self):
        self.__client.connect(self.__host, port=self.__port)
        self.__client.loop_start()

    def disconnect(self):
        self.__client.loop_stop()
        self.__client.disconnect()

    def publishConfig(self, config):
        msg = {
            'type': 'config',
            'ts': datetime.utcnow().isoformat(),
            'payload': config
        }
        self.__client.publish(self.__msg_topic, payload=json.dumps(msg))

    def publishData(self, data):
        msg = {
            'type': 'data',
            'ts': datetime.utcnow().isoformat(),
            'payload': data
        }
        self.__client.publish(self.__msg_topic, payload=json.dumps(msg))

    def publishDiag(self, diag):
        msg = {
            'type': 'system',
            'ts': datetime.utcnow().isoformat(),
            'payload': diag
        }
        self.__client.publish(self.__msg_topic, payload=json.dumps(msg))
