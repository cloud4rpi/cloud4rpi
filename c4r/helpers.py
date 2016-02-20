import re
import requests
from c4r import config
from c4r import errors
from c4r.logger import get_logger


REQUEST_TIMEOUT_SECONDS = 3 * 60 + 0.05

log = get_logger()


def request_headers(token):
    return {'api_key': token}


def device_request_url(token):
    return '{0}/devices/{1}/'.format(config.baseApiUrl, token)


def stream_request_url(token):
    return '{0}/devices/{1}/streams/'.format(config.baseApiUrl, token)


def put_device_variables(token, variables_config):
    log.info('Sending device configuration...')

    res = requests.put(device_request_url(token),
                       headers=request_headers(token),
                       json={'variables': variables_config},
                       timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    if res.status_code != 200:
        log.error('Can\'t register variables. Status: {0}'.format(res.status_code))

    return res.json()


def post_stream(token, stream):
    log.info('sending {0}'.format(stream))
    res = requests.post(stream_request_url(token),
                        headers=request_headers(token),
                        json=stream,
                        timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    return res.json()


def check_response(res):
    log.info(res.status_code)
    if res.status_code == 401:
        raise errors.AuthenticationError
    if res.status_code >= 500:
        raise errors.ServerError


def is_token_valid(token):
    r = re.compile('[0-9a-f]{24}')
    return token and len(token) == 24 and r.match(token)


def verify_token(token):
    if not is_token_valid(token):
        raise errors.InvalidTokenError


def key_exists(obj, key_name):
    return isinstance(obj, dict) and key_name in obj.keys()


def get_by_key(obj, key_name):
    if key_exists(obj, key_name):
        return obj[key_name]
    return None


def extract_variable_bind_prop(props, prop_name):
    bind = get_variable_bind(props)
    if bind is None:
        return None
    return get_by_key(bind, prop_name)


def extract_variable_prop(props, prop_name):
    return get_by_key(props, prop_name)


def get_variable_address(variable):
    return extract_variable_bind_prop(variable, 'address')


def get_variable_type(props):
    return extract_variable_bind_prop(props, 'type')


def get_variable_value(props):
    return extract_variable_prop(props, 'value')


def get_variable_bind(props):
    return extract_variable_prop(props, 'bind')


def extract_server_events(server_msg):
    if server_msg is None:
        return []
    return get_by_key(server_msg, 'newEvents')


def extract_event_payload(event):
    return get_by_key(event, 'payload')


def extract_all_payloads(new_events):
    return [extract_event_payload(x) for x in new_events]


def bind_is_instance_of(variable, cls):
    bind = get_variable_bind(variable)
    return isinstance(bind, cls)


def bind_is_handler(bind):
    if bind is None:
        return False
    return hasattr(bind, '__call__')
