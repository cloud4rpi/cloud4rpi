import requests
from c4r import mqtt
from c4r import helpers as helpers


class Transport(object):
    def send_config(self, token, config):
        pass

    def send_stream(self, token, stream):
        pass


class MqttTransport(Transport):
    @staticmethod
    def get_topic(token, name):
        return '{0}\{1}'.format(token, name)


    def send_config(self, token, config):
        mqtt.publish(MqttTransport.get_topic(token, 'config'), config)

    def post_stream(self, token, stream):
        mqtt.publish(MqttTransport.get_topic(token, 'stream'), stream)


class HttpTransport(Transport):
    def send_config(self, token, config):
        return requests.put(helpers.device_request_url(token),
                            headers=helpers.request_headers(token),
                            json=config,
                            timeout=helpers.REQUEST_TIMEOUT_SECONDS)

    def post_stream(self, token, stream):
        return requests.post(helpers.stream_request_url(token),
                             headers=helpers.request_headers(token),
                             json=stream,
                             timeout=helpers.REQUEST_TIMEOUT_SECONDS)
