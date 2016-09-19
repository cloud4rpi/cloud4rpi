from c4r import config
from c4r.logger import get_logger
import paho.mqtt.client as mqtt
import json

log = get_logger()

MQTT_ERR_SUCCESS = 0


def on_connect(client, userdata, flags, rc):
    log.debug('MQTT broker connected with result code {0}'.format(rc))


def on_disconnect(client, userdata, rc):
    if rc != MQTT_ERR_SUCCESS:
        try:
            log.debug("Attempting to reconnect...")
            client.reconnect()
        except Exception as e:
            log.debug("Reconnect error:", e.message)


def on_publish(mosq, obj, mid):
    pass


def publish(topic, stream):
    payload = json.dumps(stream)
    log.info('Publish to MQTT {0}: {1}'.format(topic, payload))
    client.publish(topic, payload, 0, True)


def connect():
    log.debug('MQTT connecting to {0}:{1}'.format(config.mqqtBrokerHost, config.mqttBrokerPort))
    client.connect(config.mqqtBrokerHost, config.mqttBrokerPort)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.username_pw_set(config.mqqtBrokerUsername, config.mqttBrokerPassword)
