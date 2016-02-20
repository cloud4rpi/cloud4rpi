from c4r import config
from c4r.logger import get_logger
import paho.mqtt.client as mqtt
import json

log = get_logger()


def on_connect(client, userdata, flags, rc):
    log.info('MQTT broker connected with result code {0}'.format(rc))

def on_disconnect(client, userdata, rc):
    log.info('MQTT broker disconnected with result code {0}'.format(rc))

def on_publish(mosq, obj, mid):
    log.info("mid: " + str(mid))

def publish(topic, stream):
    log.info('publish to mqtt broker...')
    client.publish(topic, json.dumps(stream), 0, True)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

client.username_pw_set(config.mqqtBrokerUsername, config.mqttBrokerPassword)
client.connect(config.mqqtBrokerHost, config.mqttBrokerPort)
