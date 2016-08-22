from c4r import mqtt
from c4r import helpers
from c4r.logger import get_logger

log = get_logger()


class Transport(object):
    def send_config(self, device_token, config):
        pass

    def send_stream(self, device_token, stream):
        pass

    def send_system_stream(self, device_token, stream):
        pass


class MqttTransport(Transport):
    def get_topic(self, device_token):
        return helpers.format_message_topic(device_token)

    def send_config(self, device_token, config):
        topic = self.get_topic(device_token)
        return mqtt.publish(topic, helpers.wrap_message('config', config))

    def send_stream(self, device_token, stream):
        topic = self.get_topic(device_token)
        return mqtt.publish(topic, helpers.wrap_message('data', stream))

    def send_system_stream(self, device_token, stream):
        topic = self.get_topic(device_token)
        return mqtt.publish(topic, helpers.wrap_message('system', stream))
