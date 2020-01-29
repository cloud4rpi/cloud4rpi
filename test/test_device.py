# -*- coding: utf-8 -*-

import unittest
from mock import Mock
import cloud4rpi
from cloud4rpi.errors import InvalidConfigError
from cloud4rpi.errors import UnexpectedVariableTypeError
from cloud4rpi.errors import UnexpectedVariableValueTypeError


class ApiClientMock(object):
    def __init__(self):
        def noop_on_command(cmd):
            pass

        self.publish_config = Mock()
        self.publish_data = Mock()
        self.publish_diag = Mock()
        self.on_command = noop_on_command

    def assert_publish_data_called_with(self, expected):
        return self.publish_data.assert_called_with(expected, data_type='cr')

    def raise_on_command(self, cmd):
        self.on_command(cmd)


class MockSensor(object):
    def __init__(self, value=42):
        self.read = Mock(return_value=value)
        self.__innerValue__ = value

    def get_state(self):
        return self.__innerValue__

    def get_updated_state(self, value):
        self.__innerValue__ = value
        return self.__innerValue__

    def get_incremented_state(self, value):
        return self.__innerValue__ + value


class TestDevice(unittest.TestCase):
    def testDeclareVariables(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'CPUTemp': {
                'type': 'numeric',
                'bind': MockSensor()
            }
        })
        cfg = device.read_config()
        self.assertEqual(cfg, [{'name': 'CPUTemp', 'type': 'numeric'}])

    def testDeclareVariablesValidation(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        with self.assertRaises(UnexpectedVariableTypeError):
            device.declare({
                'CPUTemp': {
                    'type': 'number',
                    'bind': MockSensor()
                }
            })

    def testDeclareDiag(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare_diag({
            'IPAddress': '8.8.8.8',
            'Host': 'hostname',
        })
        diag = device.read_diag()
        self.assertEqual(diag, {'IPAddress': '8.8.8.8', 'Host': 'hostname'})

    def testReadConfig(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'SomeVar': {
                'type': 'string'
            }
        })
        device.declare({
            'CPUTemp': {
                'type': 'numeric',
                'bind': MockSensor()
            }
        })
        cfg = device.read_config()
        self.assertEqual(cfg, [{'name': 'CPUTemp', 'type': 'numeric'}])

    def testReadConfigIfNotDeclared(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        self.assertEqual(device.read_config(), [])

    def testReadVariables(self):
        handler = {}
        temperature_sensor = MockSensor(73)
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
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
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        self.assertEqual(device.read_data(), {})

    def testReadVariablesFromClassMethod(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
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
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
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
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
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

    def testPublishConfig(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        cfg = [
            {'name': 'CPUTemp', 'type': 'numeric'},
            {'name': 'Cooler', 'type': 'bool'}
        ]
        device.publish_config(cfg)
        api.publish_config.assert_called_with(cfg)

    def testReadBeforePublishConfig(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'CPUTemp': {
                'type': 'numeric',
                'bind': MockSensor()
            }
        })
        device.publish_config()
        cfg = [{'name': 'CPUTemp', 'type': 'numeric'}]
        api.publish_config.assert_called_with(cfg)

    def testPublishConfigFail_NotAnArray(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)

        cfg = {'name': 'CPUTemp', 'type': 'numeric'}
        with self.assertRaises(InvalidConfigError):
            device.publish_config(cfg)

        api.publish_config.assert_not_called()

    def testPublishConfigFail_UnexpectedVariableType(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)

        cfg = [{'name': 'CPUTemp', 'type': 'number'}]
        with self.assertRaises(UnexpectedVariableTypeError):
            device.publish_config(cfg)

        api.publish_config.assert_not_called()

    def testPublishDiag(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        diag = {
            'IPAddress': '8.8.8.8',
            'Host': 'hostname'
        }
        device.publish_diag(diag)
        api.publish_diag.assert_called_with(diag)

    def testReadBeforePublishDiag(self):
        temperature_sensor = MockSensor(24)
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare_diag({
            'CPUTemperature': temperature_sensor,
            'IPAddress': lambda x: '8.8.8.8',
        })
        device.publish_diag()
        diag = {'IPAddress': '8.8.8.8', 'CPUTemperature': 24}
        api.publish_diag.assert_called_with(diag)

    def testPublishVariablesOnlyData(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'Temperature': {
                'type': 'numeric'
            },
            'Cooler': {
                'type': 'bool',
            }
        })
        data = {
            'Temperature': 36.6,
            'Cooler': True,
            'TheAnswer': 42
        }
        device.publish_data(data)
        api.publish_data.assert_called_with({
            'Temperature': 36.6,
            'Cooler': True
        })

    def testPublishNotDeclaredVariables(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        data = {
            'Temperature': 36.6,
            'Cooler': True,
            'TheAnswer': 42
        }
        device.publish_data(data)
        api.publish_data.assert_called_with({})

    def testReadBeforePublishData(self):
        temperature_sensor = MockSensor(24)
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'Temperature': {
                'type': 'numeric',
                'value': True,
                'bind': temperature_sensor
            }
        })
        device.publish_data()
        data = {'Temperature': 24}
        api.publish_data.assert_called_with(data)

    def testDataReadValidation_Bool(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'CoolerOn': {
                'type': 'bool',
                'value': True,
                'bind': lambda x: 100
            }
        })
        device.publish_data()
        data = {'CoolerOn': True}
        api.publish_data.assert_called_with(data)

    def testDataReadValidation_Numeric(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'ReadyState': {
                'type': 'numeric',
                'value': True,
                'bind': lambda x: True
            }
        })
        device.publish_data()
        data = {'ReadyState': 1}
        api.publish_data.assert_called_with(data)

    def testDataReadValidation_String(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'ReadyState': {
                'type': 'string',
                'value': True,
                'bind': lambda x: True
            }
        })
        device.publish_data()
        data = {'ReadyState': 'true'}
        api.publish_data.assert_called_with(data)

    def testDataReadValidation_Location(self):
        api = ApiClientMock()
        device = cloud4rpi.Device(api)
        device.declare({
            'MyLocation': {
                'type': 'location',
                'value': True,
                'bind': lambda x: {'lat': 37.89, 'lng': 75.43}
            }
        })
        device.publish_data()
        data = {'MyLocation': {'lat': 37.89, 'lng': 75.43}}
        api.publish_data.assert_called_with(data)


class CommandHandling(unittest.TestCase):
    def setUp(self):
        super(CommandHandling, self).setUp()
        self.api = ApiClientMock()
        self.device = cloud4rpi.Device(self.api)

    def testCallsBoundFunction(self):
        handler = Mock(return_value=True)
        self.device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': handler
            }
        })
        self.api.raise_on_command({'LEDOn': True})
        handler.assert_called_with(True)

    def testCallsBoundFunctionWithAnArgument(self):
        sensor = MockSensor(0)
        self.device.declare({
            'Status': {
                'type': 'numeric',
                'value': 10,
                'bind': sensor.get_updated_state
            }
        })
        self.api.raise_on_command({'Status': 20})
        self.api.assert_publish_data_called_with({'Status': 20})

    def testBindIsNotCallableFunction(self):
        self.device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': 'this is not a function'
            }
        })
        expected = {'LEDOn': True}
        self.api.raise_on_command(expected)
        self.api.assert_publish_data_called_with(expected)

        data = self.device.read_data()
        self.assertEqual(data, expected)

    def testDirectUpdateVariableValue(self):
        self.device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
            }
        })
        expected = {'LEDOn': True}
        self.api.raise_on_command(expected)
        self.api.assert_publish_data_called_with(expected)
        data = self.device.read_data()
        self.assertEqual(data, expected)

    def testSkipUnknownVariable(self):
        self.device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': lambda x: x
            }
        })
        self.api.raise_on_command({'Other': True})
        self.api.publish_data.assert_not_called()

    def testAllowPublishNullValue(self):
        self.device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': lambda x: None
            }
        })
        self.api.raise_on_command({'LEDOn': True})
        self.api.assert_publish_data_called_with({'LEDOn': None})

    def testValidateCommandValueForBool(self):
        self.device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': lambda x: x
            }
        })
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.api.raise_on_command({'LEDOn': 'false'})

    def testValidateCommandValueStringToNumeric(self):
        self.device.declare({
            'Status': {
                'type': 'numeric',
                'value': 0,
                'bind': lambda x: x
            }
        })
        self.api.raise_on_command({'Status': '100'})
        self.api.assert_publish_data_called_with({'Status': 100})

    def testValidateCommandValueUnicodeToNumeric(self):
        self.device.declare({
            'Status': {
                'type': 'numeric',
                'value': 0,
                'bind': lambda x: x
            }
        })
        unicode_val = u'38.5'
        self.api.raise_on_command({'Status': unicode_val})
        self.api.assert_publish_data_called_with({'Status': 38.5})

    def testValidateCommandValueBoolToNumeric(self):
        self.device.declare({
            'Status': {
                'type': 'numeric',
                'value': 0,
                'bind': lambda x: x
            }
        })
        self.api.raise_on_command({'Status': True})
        self.api.assert_publish_data_called_with({'Status': 1})

    def testValidateCommandValueUnicodeToString(self):
        self.device.declare({
            'Percent': {
                'type': 'string',
                'value': 0,
                'bind': lambda x: x
            }
        })
        unicode_val = u'38.5%'
        self.api.raise_on_command({'Percent': unicode_val})
        self.api.assert_publish_data_called_with({'Percent': '38.5%'})

    def testPublishBackUpdatedVariableValues(self):
        sensor = MockSensor(36.6)
        self.device.declare({
            'LEDOn': {
                'type': 'bool',
                'value': False,
                'bind': lambda x: x
            },
            'Cooler': {
                'type': 'bool',
                'value': True,
                'bind': lambda x: x
            },
            'Status': {
                'type': 'numeric',
                'value': 0,
                'bind': lambda x: 42
            },
            'Temp': {
                'type': 'numeric',
                'value': 24.4,
                'bind': sensor
            }
        })
        self.api.raise_on_command({'LEDOn': True,
                                   'Cooler': False,
                                   'Status': 2,
                                   'Temp': 36.6})
        expected = {
            'Cooler': False,
            'Status': 42,
            'LEDOn': True,
            'Temp': 36.6
        }
        self.api.assert_publish_data_called_with(expected)

    def testPublishBackOnlyCommandVariables(self):
        self.device.declare({
            'Actuator': {
                'type': 'string',
                'value': 'to be updated and published',
                'bind': lambda x: x
            },
            'Sensor': {
                'type': 'string',
                'value': None,
                'bind': 'do not updated by a command'
            },
        })
        self.api.raise_on_command({'Actuator': 'ON'})
        self.api.assert_publish_data_called_with({'Actuator': 'ON'})


class PayloadValidation(unittest.TestCase):
    def setUp(self):
        super(PayloadValidation, self).setUp()
        self.api = ApiClientMock()
        self.device = cloud4rpi.Device(self.api)

    def testNumeric(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': 36.3})
        self.api.publish_data.assert_called_with({'Temp': 36.3})

    def testNumericAsNull(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': None})
        self.api.publish_data.assert_called_with({'Temp': None})

    def testNumericAsInt(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': 36})
        self.api.publish_data.assert_called_with({'Temp': 36})

    def testNumericAsFloat(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': 36.6})
        self.api.publish_data.assert_called_with({'Temp': 36.6})

    def testNumericAsString(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': "36.6"})
        self.api.publish_data.assert_called_with({'Temp': 36.6})

    def testNumericAsBool(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': True})
        self.api.publish_data.assert_called_with({'Temp': 1.0})

    def testNumericAsNaN(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': float('NaN')})
        self.api.publish_data.assert_called_with({'Temp': None})

    def testNumericAsPositiveInfinity(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': float('Inf')})
        self.api.publish_data.assert_called_with({'Temp': None})

    def testNumericAsNegativeInfinity(self):
        self.device.declare({'Temp': {'type': 'numeric'}})
        self.device.publish_data({'Temp': -float('Inf')})
        self.api.publish_data.assert_called_with({'Temp': None})

    def testBool(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': True})
        self.api.publish_data.assert_called_with({'PowerOn': True})

    def testBoolAsNull(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': None})
        self.api.publish_data.assert_called_with({'PowerOn': None})

    def testBoolAsString(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.device.publish_data({'PowerOn': "True"})

    def testBoolAsPositiveNumber(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': 24.1})
        self.api.publish_data.assert_called_with({'PowerOn': True})

    def testBoolAsNegativeNumber(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': -10.1})
        self.api.publish_data.assert_called_with({'PowerOn': True})

    def testBoolAsZeroNumber(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': 0})
        self.api.publish_data.assert_called_with({'PowerOn': False})

    def testBoolAsNaN(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': float('NaN')})
        self.api.publish_data.assert_called_with({'PowerOn': True})

    def testBoolAsPositiveInfinity(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': float('Inf')})
        self.api.publish_data.assert_called_with({'PowerOn': True})

    def testBoolAsNegativeInfinity(self):
        self.device.declare({'PowerOn': {'type': 'bool'}})
        self.device.publish_data({'PowerOn': -float('Inf')})
        self.api.publish_data.assert_called_with({'PowerOn': True})

    def testString(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': '100'})
        self.api.publish_data.assert_called_with({'Status': '100'})

    def testStringAsNull(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': None})
        self.api.publish_data.assert_called_with({'Status': None})

    def testStringAsNumeric(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': 100.100})
        self.api.publish_data.assert_called_with({'Status': '100.1'})

    def testStringAsNaN(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': float('NaN')})
        self.api.publish_data.assert_called_with({'Status': 'nan'})

    def testStringAsPositiveInfinity(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': float('Inf')})
        self.api.publish_data.assert_called_with({'Status': 'inf'})

    def testStringAsNegativeInfinity(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': -float('Inf')})
        self.api.publish_data.assert_called_with({'Status': '-inf'})

    def testStringAsInt(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': 100})
        self.api.publish_data.assert_called_with({'Status': '100'})

    def testStringAsBool(self):
        self.device.declare({'Status': {'type': 'string'}})
        self.device.publish_data({'Status': True})
        self.api.publish_data.assert_called_with({'Status': 'true'})

    def testLocation(self):
        location = {'lat': 37.89, 'lng': 75.43}
        self.device.declare({'Pos': {'type': 'location'}})
        self.device.publish_data({'Pos': location})
        self.api.publish_data.assert_called_with({'Pos': location})

    def testLocation_Filtering(self):
        obj = {'some': 'foo', 'lng': 75.43, 'lat': 37.89, 'other': 42}
        self.device.declare({'Pos': {'type': 'location'}})
        self.device.publish_data({'Pos': obj})
        location = {'lat': 37.89, 'lng': 75.43}
        self.api.publish_data.assert_called_with({'Pos': location})

    def testLocationAsNull(self):
        self.device.declare({'Pos': {'type': 'location'}})
        self.device.publish_data({'Pos': None})
        self.api.publish_data.assert_called_with({'Pos': None})

    def testLocationAsNaN(self):
        self.device.declare({'Pos': {'type': 'location'}})
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.device.publish_data({'Pos': float('NaN')})

    def testLocationAsInfinity(self):
        self.device.declare({'Pos': {'type': 'location'}})
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.device.publish_data({'Pos': float('Inf')})

    def testLocationAsEmptyObject(self):
        self.device.declare({'Pos': {'type': 'location'}})
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.device.publish_data({'Pos': {}})

    def testLocationWithIncorrectFields(self):
        location = {'Latitude': 37.89, 'LNG': 75.43}
        self.device.declare({'Pos': {'type': 'location'}})
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.device.publish_data({'Pos': location})

    def testLocationWithoutLatitude(self):
        location = {'lng': 75.43}
        self.device.declare({'Pos': {'type': 'location'}})
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.device.publish_data({'Pos': location})

    def testLocationWithoutLongitude(self):
        location = {'lat': 37.89}
        self.device.declare({'Pos': {'type': 'location'}})
        with self.assertRaises(UnexpectedVariableValueTypeError):
            self.device.publish_data({'Pos': location})
