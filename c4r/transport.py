import requests
from c4r import mqtt
from c4r import helpers
from c4r import errors
from c4r.logger import get_logger

log = get_logger()


class Transport(object):
    def send_config(self, api_key, config):
        pass

    def send_stream(self, api_key, stream):
        pass


class MqttTransport(Transport):
    def send_config(self, api_key, config):
        return mqtt.publish(helpers.format_message_topic(api_key, 'config'), helpers.wrap_message(api_key, config))

    def send_stream(self, api_key, stream):
        return mqtt.publish(helpers.format_message_topic(api_key, 'stream'), helpers.wrap_message(api_key, stream))


class HttpTransport(Transport):
    @staticmethod
    def check_response(res):
        log.info(res.status_code)
        if res.status_code == 401:
            raise errors.AuthenticationError
        if res.status_code >= 500:
            raise errors.ServerError

    def send_config(self, api_key, config):
        res = requests.put(helpers.device_request_url(api_key),
                           headers=helpers.request_headers(api_key),
                           json=config,
                           timeout=helpers.REQUEST_TIMEOUT_SECONDS)
        HttpTransport.check_response(res)
        if res.status_code != 200:
            log.error('Can\'t register variables. Status: {0}'.format(res.status_code))

        return res.json()

    def send_stream(self, api_key, stream):
        log.info('HTTP sending {0}'.format(stream))
        res = requests.post(helpers.stream_request_url(api_key),
                            headers=helpers.request_headers(api_key),
                            json=stream,
                            timeout=helpers.REQUEST_TIMEOUT_SECONDS)
        HttpTransport.check_response(res)
        return res.json()
