from c4r import config
from c4r import helpers
from c4r import events
from c4r.logger import get_logger
import paho.mqtt.client as mqtt

KEEP_ALIVE_INTERVAL = 60 * 10

log = get_logger()

listener = None


class MqttListener(object):
    def __init__(self, api_key=''):
        self.process = None

        client_id = helpers.format_mqtt_client_id(api_key)
        self.client = mqtt.Client(client_id=client_id, clean_session=False)
        self.api_key = api_key
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def start(self):
        log.info('MqttListener - starting')
        self.connect()
        self.client.loop_start()

    def stop(self):
        if self.client is not None:
            self.client.loop_stop(force=True)
            log.info('MqttListener - listening stopped')

    def connect(self):
        log.info('Connecting to {0}:{1}'.format(config.mqqtBrokerHost, config.mqttBrokerPort))
        try:
            self.client.username_pw_set(config.mqqtBrokerUsername, config.mqttBrokerPassword)
            self.client.connect(config.mqqtBrokerHost, config.mqttBrokerPort, KEEP_ALIVE_INTERVAL)
        except Exception as e:
            log.error('Connection failed: {0}'.format(e))
            raise e

    def listen(self):
        topic = helpers.format_subscription_topic(self.api_key)
        log.info('Listen for [{0}]'.format(topic))
        self.client.subscribe(topic, qos=1)

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            log.error('Connection failed: {0}'.format(rc))
            raise Exception('Mqtt connection failed')
        self.listen()

    def on_disconnect(self, client, userdata, rc):
        log.info('MqttListener disconnected. Reason: {0}. Reconnecting ...'.format(rc))

    def on_message(self, client, userdata, message):
        log.info('[x] MQTT message received: [{0}] - [{1}]'.format(message.topic, message.payload))
        self.emit_event(message.payload)

    @staticmethod
    def emit_event(payload):
        events.on_broker_message(payload)


def start_listen(api_key):
    global listener
    if listener is None:
        listener = MqttListener(api_key)

    listener.start()


def stop_listen():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
