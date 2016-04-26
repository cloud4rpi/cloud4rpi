import datetime
import requests
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
    def send_config(self, token, config):
        return mqtt.publish(MqttTransport.get_topic('config'), MqttTransport.wrap_message(token, config))

    def send_stream(self, token, stream):
        return mqtt.publish(MqttTransport.get_topic('stream'), MqttTransport.wrap_message(token, stream))

    @staticmethod
    def get_topic(channel):
        return 'io.cloud4rpi.iot-hub.{0}'.format(channel)

    @staticmethod
    def wrap_message(token, payload):
        return {
            'token': token,
            'ts': datetime.datetime.utcnow().isoformat(),
            'payload': payload
        }


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
