import requests
from copy import copy
from c4r import mqtt
from c4r import helpers
from c4r import errors
from c4r.logger import get_logger

log = get_logger()

class Transport(object):
    def send_config(self, token, config):
        pass

    def send_stream(self, token, stream):
        pass


class MqttTransport(Transport):
    @staticmethod
    def get_topic(channel):
        return 'io.cloud4rpi.iot-hub.{0}'.format(channel)

    def send_config(self, token, config):
        message = copy(config)
        message['token'] = token
        return mqtt.publish(MqttTransport.get_topic('config'), message)

    def send_stream(self, token, stream):
        message = copy(stream)
        message['token'] = token
        return mqtt.publish(MqttTransport.get_topic('stream'), message)


class HttpTransport(Transport):
    @staticmethod
    def check_response(res):
        log.info(res.status_code)
        if res.status_code == 401:
            raise errors.AuthenticationError
        if res.status_code >= 500:
            raise errors.ServerError

    def send_config(self, token, config):
        res = requests.put(helpers.device_request_url(token),
                           headers=helpers.request_headers(token),
                           json=config,
                           timeout=helpers.REQUEST_TIMEOUT_SECONDS)
        HttpTransport.check_response(res)
        if res.status_code != 200:
            log.error('Can\'t register variables. Status: {0}'.format(res.status_code))

        return res.json()


    def send_stream(self, token, stream):
        log.info('HTTP sending {0}'.format(stream))
        res = requests.post(helpers.stream_request_url(token),
                            headers=helpers.request_headers(token),
                            json=stream,
                            timeout=helpers.REQUEST_TIMEOUT_SECONDS)
        HttpTransport.check_response(res)
        return res.json()
