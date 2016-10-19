# These tests need a running mqtt broker instance

import os
import json
import unittest
import paho.mqtt.client as mqtt
from threading import Event
from c4r.mqtt_client import MqttApi


class MqttMessageProbe(object):
    def __init__(self, on_message):
        self.__client = mqtt.Client()
        self.__on_message = on_message
        self.__client.connect('localhost')

        def on_msg(client, userdata, message):
            self.last_message = message
            on_message()

        self.__client.on_message = on_msg
        self.__client.subscribe('iot-hub/messages/#')
        self.__client.loop_start()


class TimeoutError(Exception):
    pass


class AsyncTestCase(unittest.TestCase):
    def setUp(self):
        super(AsyncTestCase, self).setUp()
        self._done = Event()
        self._done.clear()

    def tearDown(self):
        super(AsyncTestCase, self).tearDown()
        self._done.clear()

    def wait(self, timeout=None):
        if timeout is None:
            timeout = get_async_test_timeout()

        self._done.wait(timeout)

        if not self.is_done():
            raise TimeoutError()

    def stop(self):
        self._done.set()

    def is_done(self):
        return self._done.isSet()


def get_async_test_timeout(default=5):
    try:
        return float(os.environ.get('ASYNC_TEST_TIMEOUT'))
    except (ValueError, TypeError):
        return default


class TestTemp(AsyncTestCase):
    # TODO: setUp/tearDown

    def testAsyncTest(self):
        client = mqtt.Client(client_id='c4r-unique-device-token')

        def on_connect(*args):
            self.stop()

        client.on_connect = on_connect

        client.connect('localhost')
        client.loop_start()

        self.wait()

        client.loop_stop()
        client.disconnect()

    def testPublishConfig(self):
        test_probe = MqttMessageProbe(on_message=lambda: self.stop())

        client = MqttApi('c4r-unique-device-token')
        client.connect()

        variables = [
            {'name': 'Temperature', 'type': 'numeric'},
            {'name': 'Cooler', 'type': 'bool'},
            {'name': 'TheAnswer', 'type': 'numeric'},
        ]
        client.publishConfig(variables)

        self.wait()

        actual_msg = test_probe.last_message
        self.assertEqual('iot-hub/messages/c4r-unique-device-token', actual_msg.topic)
        self.assertEqual('config', json.loads(actual_msg.payload)['type'])
        self.assertEqual(variables, json.loads(actual_msg.payload)['payload'])

    def testPublishData(self):
        test_probe = MqttMessageProbe(on_message=lambda: self.stop())

        client = MqttApi('c4r-unique-device-token')
        client.connect()

        data = {
            'Temperature': 36.6,
            'Cooler': True,
            'TheAnswer': 42
        }
        client.publishData(data)

        self.wait()

        actual_msg = test_probe.last_message
        self.assertEqual('iot-hub/messages/c4r-unique-device-token', actual_msg.topic)
        self.assertEqual('data', json.loads(actual_msg.payload)['type'])
        self.assertEqual(data, json.loads(actual_msg.payload)['payload'])

    def testPublishDiag(self):
        test_probe = MqttMessageProbe(on_message=lambda: self.stop())

        client = MqttApi('c4r-unique-device-token')
        client.connect()

        diag = {
            'IPAddress': '127.0.0.1',
            'Hostname': 'weather_station',
            'CPU Load': 99
        }
        client.publishDiag(diag)

        self.wait()

        actual_msg = test_probe.last_message
        self.assertEqual('iot-hub/messages/c4r-unique-device-token', actual_msg.topic)
        self.assertEqual('system', json.loads(actual_msg.payload)['type'])
        self.assertEqual(diag, json.loads(actual_msg.payload)['payload'])
