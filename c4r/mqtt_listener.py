from c4r import config
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


    def start(self, device_token):
        self.connect()
        self.listen(device_token)
        self.client.loop_start()
        log.info('MqttListener - listening started')

    def stop(self):
        if self.client is not None:
            self.client.loop_stop(force=True)
            log.info('MqttListener - listening stopped')

    def connect(self):
        log.info('MQTT connecting to {0}:{1}'.format(config.mqqtBrokerHost, config.mqqtBrokerHost))
        try:
            self.client.username_pw_set(config.mqqtBrokerUsername, config.mqttBrokerPassword)
            self.client.connect(config.mqqtBrokerHost, config.mqqtBrokerHost)
        except Exception as e:
            log.error('Connection failed: {0}'.format(e))
            raise e

    def listen(self, device_token):
        topic = '{0}/events'.format(device_token)
        log.info('subscribing for [{0}]'.format(topic))
        self.client.subscribe(topic, 0)

    def on_message(self, client, userdata, message):
        log.info('MQTT message received: [{0}] -[{1}]'.format(message.topic, message.payload))
        raise_event(message.payload)


listener = None


def start_listen(device_token):
    global listener
    if listener is None:
        listener = MqttListener()

    listener.start(device_token)


def stop_listen():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
