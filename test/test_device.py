# -*- coding: utf-8 -*-

import unittest
import cloud4rpi

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
        self.__innerValue__ = value

    def get_state(self):
        return self.__innerValue__

    def get_incremented_state(self, value):
        return self.__innerValue__ + value


class TestDevice(unittest.TestCase):
    def testDeclareVariables(self):
        device = cloud4rpi.Device()
        device.declare({
            'CPUTemp': {
                'type': 'numeric',
                'bind': MockSensor()
            }
        })
        cfg = device.read_config()
        self.assertEqual(cfg, [{'name': 'CPUTemp', 'type': 'numeric'}])

    def testReadConfig(self):
        device = cloud4rpi.Device()
        device.declare({
            'CPUTemp': {
                'type': 'numeric',
                'bind': MockSensor()
            }
        })
        cfg = device.read_config()
        self.assertEqual(cfg, [{'name': 'CPUTemp', 'type': 'numeric'}])

    def testReadConfigIfNotDeclared(self):
        device = cloud4rpi.Device()
        self.assertEqual(device.read_config(), [])

    def testCallsBoundFunctionOnCommand(self):
        handler = Mock()
        device = cloud4rpi.Device()
        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': handler
            }
        })
        device.apply_commands({'LEDOn': True})
        handler.assert_called_with(True)

    def testSendsBackActualVarValuesOnCommand(self):
        api = ApiClientMock()
        device = cloud4rpi.Device()

        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': lambda x: True
            },
            'Cooler': {
                'type': 'bool',
                'value': True,
                'bind': lambda x: False
            }
        })
        api.on_command = device.handle_mqtt_commands(api)
        api.raise_on_command({'LEDOn': True, 'Cooler': False})

        self.assertEqual(device.read_data(), {
            'LEDOn': True,
            'Cooler': False
        })

        api.publish_data.assert_called_with({
            'LEDOn': True,
            'Cooler': False
        })

    def testSkipsVarIfItsBindIsNotAFunctionOnCommand(self):
        api = ApiClientMock()
        device = cloud4rpi.Device()
        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': 'this is not a function'
            }
        })
        api.on_command = device.handle_mqtt_commands(api)
        api.raise_on_command({'LEDOn': True})

        # consider behavior in the case of the incorrect bind implementation
        data = device.read_data()
        # result of conversation 'this is not a function' to bool
        self.assertEqual(data, {
            'LEDOn': True  # False
        })
        # api.publish_data.assert_not_called()

    def testReadVariables(self):
        handler = {}
        temperature_sensor = MockSensor(73)
        device = cloud4rpi.Device()
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
        data = device.read_data()
        self.assertEqual(data, {
            'LEDOn': False,
            'Temperature': 73
        })

    def testReadVariablesDoesNotContainsEmptyVars(self):
        device = cloud4rpi.Device()
        self.assertEqual(device.read_data(), {})

    def testReadVariablesAfterCommandApplied(self):
        device = cloud4rpi.Device()

        device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': lambda x: True
            },
            'Cooler': {
                'type': 'bool',
                'value': True,
                'bind': lambda x: False
            }
        })
        device.apply_commands({'LEDOn': True, 'Cooler': False})
        data = device.read_data()
        self.assertEqual(data, {
            'LEDOn': True,
            'Cooler': False
        })

    def testReadVariablesFromClassMethod(self):
        device = cloud4rpi.Device()
        sensor = MockSensor(10)

        device.declare({
            'MyParam': {
                'type': 'numeric',
                'bind': sensor.get_state
            },
        })
        data = device.read_data()
        self.assertEqual(data, {
            'MyParam': 10,
        })

    def testReadVariablesFromClassMethodWithCurrent(self):
        device = cloud4rpi.Device()
        sensor = MockSensor(10)

        device.declare({
            'MyParam': {
                'type': 'numeric',
                'value': 1,
                'bind': sensor.get_incremented_state
            },
        })
        data = device.read_data()
        self.assertEqual(data, {
            'MyParam': 11,
        })

    def testReadDiag(self):
        temperature_sensor = MockSensor(73)
        device = cloud4rpi.Device()
        device.declare_diag({
            'CPUTemperature': temperature_sensor,
            'IPAddress': lambda x: '8.8.8.8',
            'OSName': lambda x: 'Linux',
            'Host': 'weather_station'
        })
        diag = device.read_diag()
        self.assertEqual(diag, {
            'CPUTemperature': 73,
            'IPAddress': '8.8.8.8',
            'OSName': 'Linux',
            'Host': 'weather_station'
        })
