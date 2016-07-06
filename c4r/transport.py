from c4r import mqtt
from c4r import helpers
from c4r.logger import get_logger

log = get_logger()


class Transport(object):
    def send_config(self, api_key, config):
        pass

    def send_stream(self, api_key, stream):
        pass

    def send_system_stream(self, api_key, stream):
        pass


class MqttTransport(Transport):
    def get_topic(self, api_key):
        return helpers.format_message_topic(api_key)

    def send_config(self, api_key, config):
        topic = self.get_topic(api_key)
        return mqtt.publish(topic, helpers.wrap_message('config', config))

    def send_stream(self, api_key, stream):
        topic = self.get_topic(api_key)
        return mqtt.publish(topic, helpers.wrap_message('data', stream))

    def send_system_stream(self, api_key, stream):
        topic = self.get_topic(api_key)
        return mqtt.publish(topic, helpers.wrap_message('system', stream))
