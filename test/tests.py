#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import types
import unittest
from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner
import os  # should be imported before fake_filesystem_unittest
import c4r
from c4r import lib
from c4r import ds18b20 as ds_sensors
from c4r.cpu import Cpu
from c4r.ds18b20 import W1_DEVICES
from c4r import helpers
from c4r import transport
from c4r import errors
from c4r import mqtt
from c4r import mqtt_listener
import pyfakefs.fake_filesystem_unittest as fake_filesystem_unittest
from mock import patch
from mock import MagicMock


api_key = '00000000-0000-4000-a000-000000000000'

sensor_10 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=22250'

sensor_28 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=28250'


class TestApi(unittest.TestCase):
    def setUp(self):
        c4r.set_api_key(api_key)

    @staticmethod
    @patch('c4r.lib.read_persistent')
    def testReadPersistent(mock):
        var = {'A': 1}
        c4r.read_persistent(var)
        mock.assert_called_once_with({'A': 1})

    @staticmethod
    @patch('c4r.lib.read_system')
    def testReadSystem(mock):
        var = {'A': 1}
        c4r.read_system(var)
        mock.assert_called_once_with({'A': 1})

    @patch('c4r.ds18b20.find_all')
    def testFindDSSensors(self, mock):
        c4r.find_ds_sensors()
        self.assertTrue(mock.called)

    def call_without_token(self, methods):
        lib.api_key = None
        for fn, args in methods.items():
            with self.assertRaises(errors.InvalidTokenError):
                if args is None:
                    fn()
                else:
                    fn(*args)

    def testVerifyToken(self):
        methods = {
            c4r.register: ({},),
            c4r.send_receive: ({},)
        }
        self.call_without_token(methods)


class TestLibrary(unittest.TestCase):
    sensorReadingMock = None

    def setUp(self):
        pass

    def tearDown(self):
        self.restoreSensorReadingMock()

    def setUpSensorReading(self, expected_val):
        self.restoreSensorReadingMock()
        self.sensorReadingMock = MagicMock(return_value=expected_val)
        ds_sensors.read = self.sensorReadingMock

    def restoreSensorReadingMock(self):
        if not self.sensorReadingMock is None:
            self.sensorReadingMock.reset_mock()

    def methods_exists(self, methods):
        for m in methods:
            self.assertTrue(inspect.ismethod(m))

    def static_methods_exists(self, methods):
        for m in methods:
            is_instance = isinstance(m, types.FunctionType)
            self.assertTrue(is_instance)

    def testDefauls(self):
        self.assertIsNone(lib.api_key)


    def testStaticMethodsExists(self):
        self.static_methods_exists([
            lib.set_api_key,
            lib.run_handler,
            lib.find_ds_sensors,
            lib.create_ds18b20_sensor,
            lib.read_persistent,
            lib.send_receive
        ])

    def testSetApiKey(self):
        self.assertIsNone(lib.api_key)
        lib.set_api_key(api_key)
        self.assertEqual(lib.api_key, api_key)

    def testHandlerExists(self):
        var1 = {
            'title': 'valid',
            'bind': MockHandler.empty
        }
        var2 = {
            'title': 'invalid',
            'bind': {'address': 'abc'}
        }
        self.assertFalse(lib.bind_handler_exists(None))
        self.assertFalse(lib.bind_handler_exists(var2))
        self.assertTrue(lib.bind_handler_exists(var1))


    @staticmethod
    @patch('c4r.ds18b20.read')
    def testReadPersistent(mock):
        addr = '10-000802824e58'
        body = {
            'title': 'temp',
            'bind': {
                'type': 'ds18b20',
                'address': addr
            }
        }
        variables = {"Var1": body}

        lib.read_persistent(variables)
        mock.assert_called_with(addr)

    @staticmethod
    @patch('c4r.lib.read_cpu')
    def testReadSystemOnlyWithCpu(mock):
        cpuObj = Cpu()
        variables = {
            'any': {'title': 'abc'},
            'CPU': {'title': 'cpu_temp', 'bind': cpuObj},
            'noCPU': {'title': 'no_bind'}
        }
        lib.read_system(variables)
        mock.assert_called_with({'title': 'cpu_temp', 'bind': cpuObj})


    @patch.object(Cpu, 'read')
    def testReadCpu(self, mock):
        mock.return_value = 0
        cpuObj = Cpu()
        cpuObj.get_temperature = MagicMock(return_value=36.6)

        cpuVar = {'title': 'cpu_temp', 'bind': cpuObj}

        self.assertFalse(cpuVar.has_key('value'))
        lib.read_cpu(cpuVar)
        self.assertEqual(cpuVar['value'], 36.6)


    def testUpdateVariableValueOnRead(self):
        addr = '10-000802824e58'
        var = {
            'title': 'temp',
            'bind': {'type': 'ds18b20', 'address': addr}
        }
        variables = {'Test': var}

        self.setUpSensorReading(22.4)

        lib.read_persistent(variables)
        self.assertEqual(var['value'], 22.4)

    # TODO discuss
    # def testCollectReadings(self):
    # variables = {
    # 'temp1': {'title': '123', 'value': 22.4, 'bind': {'type': 'ds18b20'}},
    # 'some': {'title': '456', 'bind': {'type': 'unknown'}},
    # 'temp2': {'title': '456', 'bind': {'type': 'ds18b20'}}
    #     }
    #     readings = lib.collect_readings(variables)
    #     expected = {'temp2': None, 'temp1': 22.4}
    #     self.assertEqual(readings, expected)


    @patch.object(Cpu, 'read')
    def testCollectCpuTemperatureReadings(self, mock):
        mock.return_value = 0
        cpuObj = Cpu()
        cpuObj.get_temperature = MagicMock(return_value=36.6)
        variables = {
            'CPU': {'title': 'cpu_temp', 'bind': cpuObj}
        }
        lib.read_cpu(variables['CPU'])
        readings = lib.collect_readings(variables)
        expected = {'CPU': 36.6}
        self.assertEqual(readings, expected)


class TestFileSystemAndRequests(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.patchRequests()
        self.fs.CreateFile('/dev/null')

    def setUpResponse(self, verb, response, status_code=200):
        r_mock = MagicMock(['json', 'status_code'])
        r_mock.json.return_value = response
        verb.return_value = r_mock
        self.setUpStatusCode(verb, status_code)

    @staticmethod
    def setUpDefaultHttpTransport():
        r_mock = MagicMock()
        r_mock.return_value = transport.HttpTransport()
        lib.get_active_transport = r_mock

    @staticmethod
    def setUpStatusCode(verb, code):
        verb.return_value.status_code = code

    def patchRequests(self):
        self.get = self.startPatching('requests.get')
        self.put = self.startPatching('requests.put')
        self.post = self.startPatching('requests.post')

    def setUpDefaultResponses(self):
        self.setUpPOSTStatus(201)


    @staticmethod
    def startPatching(target):
        return patch(target).start()

    def setUpGET(self, res_body):
        self.setUpResponse(self.get, res_body)

    def setUpPUT(self, res_body):
        self.setUpResponse(self.put, res_body)

    def setUpGETStatus(self, code):
        self.setUpStatusCode(self.get, code)

    def setUpPUTStatus(self, code):
        self.setUpStatusCode(self.put, code)

    def setUpPOSTStatus(self, code):
        self.setUpStatusCode(self.post, code)


class TestDataExchange(TestFileSystemAndRequests):
    def setUp(self):
        super(TestDataExchange, self).setUp()
        self.setUpDefaultResponses()
        self.setUpDefaultHttpTransport()
        lib.set_api_key(api_key)

    def tearDown(self):
        lib.set_api_key(None)

    def testSendReceive(self):
        variables = {
            'temp1': {'title': '123', 'value': 22.4, 'bind': {'type': 'ds18b20', 'address': '10-000802824e58'}}
        }
        self.setUpResponse(self.post, variables, 201)
        json = lib.send_receive(variables)
        self.assertEqual(json, variables)

    def testRaiseExceptionOnUnAuthStreamPostRequest(self):
        self.setUpPOSTStatus(401)
        with self.assertRaises(errors.AuthenticationError):
            lib.send_receive({})

    @staticmethod
    @patch('c4r.transport.HttpTransport.send_config')
    def test_register_variables(mock):
        variables = {
            'var1': {
                'title': 'temp',
                'type': 'number',
                'bind': 'ds18b20'
            }
        }
        c4r.register(variables)
        mock.assert_called_with(api_key, {'variables': [{'type': 'number', 'name': 'var1'}]})


class TestHelpers(unittest.TestCase):
    def testExtractVariableBindAttr(self):
        addr = '10-000802824e58'
        bind = {
            'address': addr,
            'value': 22
        }
        var = {
            'title': 'temp',
            'bind': bind
        }
        actual = helpers.extract_variable_bind_prop(var, 'address')
        self.assertEqual(actual, addr)

    def testBindIsCPUInstance(self):
        obj = Cpu()
        variables = {
            'CPU': {'title': 'cpu_temp', 'bind': obj},
            'NoCPU': {'title': 'no_cpu', 'bind': None}
        }
        self.assertTrue(helpers.bind_is_instance_of(variables['CPU'], Cpu))
        self.assertFalse(helpers.bind_is_instance_of(variables['CPU'], MagicMock))
        self.assertFalse(helpers.bind_is_instance_of(variables['NoCPU'], Cpu))

    def testBindIsHandler(self):
        variables = {
            'var1': {'title': 'with', 'bind': MockHandler.empty},
            'var2': {'title': 'without', 'bind': None},
            'var3': {'title': 'without', 'bind': 'Something'}
        }
        self.assertTrue(helpers.bind_is_handler(variables['var1']['bind']))
        self.assertFalse(helpers.bind_is_handler(variables['var2']['bind']))
        self.assertFalse(helpers.bind_is_handler(variables['var3']['bind']))

    def testExtractSrverEvents(self):
        server_msg = {
            'newEvents': [
                {'Cooler': 1},
                {'OFF': 0}
            ]
        }
        events = helpers.extract_server_events(server_msg)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0], {'Cooler': 1})
        self.assertEqual(events[1], {'OFF': 0})

    def testJoinStrings(self):
        self.assertEqual('a/b/c', helpers.join_strings(['a', 'b', 'c']))

    def testFormatMessagesTopic(self):
        result = helpers.format_message_topic('test-api-key', 'params')
        self.assertEqual(result, 'iot-hub/messages/test-api-key/params')

    def testFormatSubscriptionTopic(self):
        result = helpers.format_subscription_topic('ledOn')
        self.assertEqual(result, 'iot-hub/commands/ledOn')

    def testIsTokenValid(self):
        self.assertFalse(helpers.is_token_valid('5693813ab288f00b4cb31904'))

        self.assertFalse(helpers.is_token_valid('00000000-0000-3000-c000-000000000000'))
        self.assertFalse(helpers.is_token_valid('00000000-0000-4000-0000-000000000000'))
        self.assertFalse(helpers.is_token_valid('00000000-0000-0000-b000-000000000000'))

        self.assertTrue(helpers.is_token_valid('a5751fc6-0ed0-4e77-ba40-b2a410b15e26'))


class TestDs18b20Sensors(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def setUpSensor(self, address, content):
        self.fs.CreateFile(os.path.join(W1_DEVICES, address, 'w1_slave'), contents=content)

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)

    def testCreate_ds18b20_sensor(self):
        sensor = lib.create_ds18b20_sensor('abc')
        self.assertEqual(sensor, {'address': 'abc', 'type': 'ds18b20'})

    def testFindDSSensors(self):
        self.setUpSensors()
        sensors = lib.find_ds_sensors()
        self.assertTrue(len(sensors) > 0)
        expected = [
            {'address': '10-000802824e58', 'type': 'ds18b20'},
            {'address': '28-000802824e58', 'type': 'ds18b20'}
        ]
        self.assertEqual(sensors, expected)


class MockHandler(object):
    @staticmethod
    def variable_inc_val(var):
        var['value'] += 1

    @staticmethod
    def empty(var):
        pass


class TestEvents(unittest.TestCase):
    def testOnBrokerMessage(self):
        self.call_args = None
        c4r.on_broker_message += self.messageHandler

        mqtt_listener.raise_event('test42')
        self.assertEqual(self.call_args[0], 'test42')

        self.call_args = None
        c4r.on_broker_message -= self.messageHandler
        mqtt_listener.raise_event('other')
        self.assertEqual(self.call_args, None)


    def messageHandler(self, *args, **kwargs):
        self.call_args = args


class ErrorMessages(unittest.TestCase):
    def testGetErrorMessage(self):
        m = c4r.get_error_message(KeyboardInterrupt('test_key_err'))
        self.assertEqual(m, 'Interrupted')
        m = c4r.get_error_message(c4r.errors.ServerError('crash'))
        self.assertEqual(m, 'Unexpected error: crash')
        m = c4r.get_error_message(c4r.errors.AuthenticationError())
        self.assertEqual(m, 'Authentication failed. Check your API key.')


def main():
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)


if __name__ == '__main__':
    main()
