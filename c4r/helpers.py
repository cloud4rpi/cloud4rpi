import datetime
import re
from c4r import config
from c4r import errors
from c4r.logger import get_logger


REQUEST_TIMEOUT_SECONDS = 3 * 60 + 0.05

log = get_logger()


def is_token_valid(token):
    r = re.compile('[1-9a-km-zA-HJ-NP-Z]{23,}')
    return token and r.match(token)


def verify_token(token):
    if not is_token_valid(token):
        raise errors.InvalidTokenError(token)


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


def variable_of_type(variable, type_value):
    return extract_variable_prop(variable, 'type') == type_value


def set_bool_variable_value(variable, value):
    variable['value'] = bool(value) if variable_of_type(variable, 'bool') else value


def get_variable_address(variable):
    return extract_variable_bind_prop(variable, 'address')


def get_variable_type(props):
    return extract_variable_bind_prop(props, 'type')


def get_variable_value(props):
    return extract_variable_prop(props, 'value')


def get_variable_bind(props):
    return extract_variable_prop(props, 'bind')


def extract_server_events(server_msg):  # only for http-data-exchange scenario
    if server_msg is None:
        return []
    return get_by_key(server_msg, 'newEvents')


def extract_event_payload(event):
    return get_by_key(event, 'payload')


def extract_all_payloads(new_events):
    return [extract_event_payload(x) for x in new_events]


def bind_is_handler(bind):
    if bind is None:
        return False
    return hasattr(bind, '__call__')


def bind_is_instance_of(variable, cls):
    bind = get_variable_bind(variable)
    return isinstance(bind, cls)


def join_strings(args):
    return '/'.join(args)


def format_message_topic(device_token):
    return join_strings([config.mqttMessageTopicPrefix, device_token])


def format_subscription_topic(device_token):
    return join_strings([config.mqttCommandsTopicPrefix, device_token])


def format_mqtt_client_id(device_token):
    return 'c4r-{0}-'.format(device_token)


def wrap_message(message_type, payload):
    return {
        'type': message_type,
        'ts': datetime.datetime.utcnow().isoformat(),
        'payload': payload
    }
