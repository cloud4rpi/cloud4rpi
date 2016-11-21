# -*- coding: utf-8 -*-

import unittest
import cloud4rpi.device

from mock import Mock


class ApiClientMock(object):
    def __init__(self):
        def noop_on_command(cmd):
            pass

        self.publish_config = Mock()
        self.publish_data = Mock()
        self.publish_diag = Mock()
        self.on_command = noop_on_command

    def raise_on_command(self, cmd):
        self.on_command(cmd)


class MockSensor(object):
    def __init__(self, value=42):
        self.read = Mock(return_value=value)


class DiagFuncMock(object):
    @staticmethod
    def ip_address():
        return '8.8.8.8'

    @staticmethod
    def osname():
        return 'Linux'


class TestDevice(unittest.TestCase):
    def testDeclareVariables(self):
        api = ApiClientMock()
        device = cloud4rpi.device.Device(api)
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
        device = cloud4rpi.device.Device(api)
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
        device = cloud4rpi.device.Device(api)
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
        device = cloud4rpi.device.Device(api)
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
        handler = {}
        temperature_sensor = MockSensor(73)
        device = cloud4rpi.device.Device(api)
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
        device = cloud4rpi.device.Device(api)
        device.send_data()
        api.publish_data.assert_not_called()

    def testSendDataAfterCommand(self):
        api = ApiClientMock()
        led_handler = Mock(return_value=True)
        del led_handler.read
        cooler_handler = Mock(return_value=False)
        del cooler_handler.read
        device = cloud4rpi.device.Device(api)
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
        device = cloud4rpi.device.Device(api)
        device.declare_diag({
            'CPUTemperature': temperature_sensor,
            'IPAddress': DiagFuncMock.ip_address,
            'OSName': DiagFuncMock.osname(),
            'Host': 'weather_station'
        })
        device.send_diag()
        api.publish_diag.assert_called_with({
            'CPUTemperature': 73,
            'IPAddress': '8.8.8.8',
            'OSName': 'Linux',
            'Host': 'weather_station'
        })
