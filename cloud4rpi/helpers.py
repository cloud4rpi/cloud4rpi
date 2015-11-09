import json
import os
import re
import requests
import cloud4rpi.errors as errors
from cloud4rpi.server_device import ServerDevice
from cloud4rpi.__main__ import log
import settings_vendor as config
from sensors import cpu as cpu_sensor


REQUEST_TIMEOUT_SECONDS = 3 * 60 + 0.05


def find_actuators(settings):
    return [x['address'] for x in settings.Actuators]


def find_variables(settings):
    return [x['name'] for x in settings.Variables]


def request_headers(token):
    return {'api_key': token}


def device_request_url(token):
    return '{0}/devices/{1}/'.format(config.baseApiUrl, token)


def stream_request_url(token):
    return '{0}/devices/{1}/streams/'.format(config.baseApiUrl, token)


def system_parameters_request_url(token):
    return '{0}/devices/{1}/params/'.format(config.baseApiUrl, token)


def actuator_param_request_url(actuator_id):
    return '{0}/actuators/{1}/param'.format(config.baseApiUrl, actuator_id)


def get_system_parameters():
    cpu_temperature = cpu_sensor.read()
    return {
        'cpuTemperature': cpu_temperature
    }


def get_device(token):
    if os.path.isfile(config.config_file):
        try:
            with open(config.config_file, 'r') as config_file:
                device = json.load(config_file)

            return ServerDevice(device)
        except (TypeError, Exception) as e:
            log.exception('Error during load saved device config. Skipping... Error: {0}'.format(e.message))

    res = requests.get(device_request_url(token),
                       headers=request_headers(token),
                       timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    return ServerDevice(res.json())


def put_device(token, device):
    log.info('Sending device configuration...')
    device_json = device.dump()
    log.info('DEVICE: ' + str(device_json))
    res = requests.put(device_request_url(token),
                       headers=request_headers(token),
                       json=device_json,
                       timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    if res.status_code != 200:
        log.error("Can't register sensor. Status: {0}".format(res.status_code))

    http_result = res.json()
    with open(config.config_file, 'w') as config_file:
        json.dump(http_result, config_file)

    return ServerDevice(http_result)


def post_stream(token, stream):
    log.info('sending {0}'.format(stream))

    res = requests.post(stream_request_url(token),
                        headers=request_headers(token),
                        json=stream,
                        timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    return res.json()


def post_system_parameters(token):
    params = get_system_parameters()
    log.info('sending {0}'.format(params))

    res = requests.post(system_parameters_request_url(token),
                        headers=request_headers(token),
                        json=params,
                        timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    return res.json()


def get_actuator_state(token, actuator_id):
    res = requests.get(actuator_param_request_url(actuator_id),
                       params={'name': 'state'},
                       headers=request_headers(token),
                       timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    return res.json()


def set_actuator_state(token, actuator_id, state):
    res = requests.post(actuator_param_request_url(actuator_id),
                        params={'name': 'state', 'value': state},
                        headers=request_headers(token),
                        timeout=REQUEST_TIMEOUT_SECONDS)
    check_response(res)
    return res.json()


def check_response(res):
    log.info(res.status_code)
    if res.status_code == 401:
        raise errors.AuthenticationError


def verify_token(token):
    r = re.compile('[0-9a-f]{24}')
    return len(token) == 24 and r.match(token)
