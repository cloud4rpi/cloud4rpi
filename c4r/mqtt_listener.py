from c4r import config
from c4r import helpers
from c4r import events
from c4r.logger import get_logger
import paho.mqtt.client as mqtt

log = get_logger()


def raise_event(content):
    events.on_broker_message(content)


class MqttListener(object):
    def __init__(self):
        self.process = None
        self.client = mqtt.Client()
        self.client.on_message = self.on_message


    def start(self, api_key):
        log.info('MqttListener - starting')
        self.connect()
        self.listen(api_key)
        self.client.loop_start()
        log.info('MqttListener - listening started')

    def stop(self):
        if self.client is not None:
            self.client.loop_stop(force=True)
            log.info('MqttListener - listening stopped')

    def connect(self):
        log.info('MqttListener connecting to {0}:{1}'.format(config.mqqtBrokerHost, config.mqttBrokerPort))
        try:
            self.client.username_pw_set(config.mqqtBrokerUsername, config.mqttBrokerPassword)
            self.client.connect(config.mqqtBrokerHost, config.mqttBrokerPort)
        except Exception as e:
            log.error('Connection failed: {0}'.format(e))
            raise e

    def listen(self, api_key):
        s = 'events/{1}'.format(api_key)
        topic = helpers.format_mq_topic(s)

        log.info('subscribing for [{0}]'.format(topic))
        self.client.subscribe(topic, 0)

    def on_message(self, client, userdata, message):
        log.info('MQTT message received: [{0}] - [{1}]'.format(message.topic, message.payload))
        raise_event(message.payload)


listener = MqttListener()


def start_listen(api_key):
    global listener
    if listener is None:
        listener = MqttListener()

    listener.start(api_key)


def stop_listen():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
