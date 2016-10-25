# -*- coding: utf-8 -*-

import c4r.device
import unittest
from mock import Mock


class ApiClientMock(object):
    def __init__(self):
        self.publish_config = Mock()
        self.publish_data = Mock()
        self.publish_diag = Mock()

    def raise_on_command(self, cmd):
        self.on_command(cmd)


class MockSensor(object):
    def __init__(self, value=42):
        self.read = Mock(return_value=value)


class TestDevice(unittest.TestCase):
    def testDeclareVariables(self):
        api = ApiClientMock()
        device = c4r.device.Device(api)
        device.declare({
            'CPUTemp': {
                'type': 'numeric',
                'bind': MockSensor()
            }
        })
        api.publish_config.assert_called_with([
            {'name': 'CPUTemp', 'type': 'numeric'}
        ])

    def testCallsBoundFunctionOnCommand(self):
        api = ApiClientMock()
        handler = Mock()
        device = c4r.device.Device(api)
        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': handler
            }
        })
        api.raise_on_command({'LEDOn': True})
        handler.assert_called_with(True)

    def testSendsBackActualVarValuesOnCommand(self):
        api = ApiClientMock()
        led_handler = Mock(return_value=True)
        cooler_handler = Mock(return_value=False)
        device = c4r.device.Device(api)
        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': led_handler
            },
            'Cooler': {
                'type': 'bool',
                'value': True,
                'bind': cooler_handler
            }
        })
        api.raise_on_command({'LEDOn': True, 'Cooler': False})
        api.publish_data.assert_called_with({
            'LEDOn': True,
            'Cooler': False
        })

    def testSkipsVarIfItsBindIsNotAFunctionOnCommand(self):
        api = ApiClientMock()
        device = c4r.device.Device(api)
        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': 'this is not a function'
            }
        })
        api.raise_on_command({'LEDOn': True})

    def testSendData(self):
        api = ApiClientMock()
        handler = Mock()
        del handler.read
        temperature_sensor = MockSensor(73)
        device = c4r.device.Device(api)
        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': handler
            },
            'Temperature': {
                'type': 'numeric',
                'value': True,
                'bind': temperature_sensor
            }
        })
        device.send_data()
        api.publish_data.assert_called_with({
            'LEDOn': False,
            'Temperature': 73
        })

    def testSendDataDoesNotSendEmptyVars(self):
        api = ApiClientMock()
        device = c4r.device.Device(api)
        device.send_data()
        api.publish_data.assert_not_called()

    def testSendDataAfterCommand(self):
        api = ApiClientMock()
        led_handler = Mock(return_value=True)
        del led_handler.read
        cooler_handler = Mock(return_value=False)
        del cooler_handler.read
        device = c4r.device.Device(api)
        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': led_handler
            },
            'Cooler': {
                'type': 'bool',
                'value': True,
                'bind': cooler_handler
            }
        })
        api.raise_on_command({'LEDOn': True, 'Cooler': False})
        api.publish_data.reset_mock()
        device.send_data()
        api.publish_data.assert_called_with({
            'LEDOn': True,
            'Cooler': False
        })

    def testSendDiag(self):
        api = ApiClientMock()
        temperature_sensor = MockSensor(73)
        device = c4r.device.Device(api)
        device.declare_diag({
            'CPUTemperature': temperature_sensor,
            'IPAddress': '127.0.0.1',
            'Host': 'weather_station'
        })
        device.send_diag()
        api.publish_diag.assert_called_with({
            'CPUTemperature': 73,
            'IPAddress': '127.0.0.1',
            'Host': 'weather_station'
        })
