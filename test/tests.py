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
from c4r.cpu_temperature import CpuTemperature
from c4r.net import NetworkInfo
from c4r.transport import MqttTransport
from c4r.ds18b20 import W1_DEVICES
from c4r import helpers
from c4r import errors
from c4r import mqtt_listener
import pyfakefs.fake_filesystem_unittest as fake_filesystem_unittest
from mock import patch
from mock import MagicMock

device_token = '00000000-0000-4000-a000-000000000000'

sensor_10 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=22250'

sensor_28 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=28250'


class TestApi(unittest.TestCase):
    def setUp(self):
        c4r.set_device_token(device_token)

    @staticmethod
    @patch('c4r.lib.read_variables')
    def testReadVariables(mock):
        var = {'A': 1}
        c4r.read_variables(var)
        mock.assert_called_once_with({'A': 1})

    @patch('c4r.ds18b20.find_all')
    def testFindDSSensors(self, mock):
        c4r.find_ds_sensors()
        self.assertTrue(mock.called)

    def call_without_token(self, methods):
        lib.device_token = None
        for fn, args in methods.items():
            with self.assertRaises(errors.InvalidTokenError):
                if args is None:
                    fn()
                else:
                    fn(*args)

    def testVerifyToken(self):
        methods = {
            c4r.register: ({},),
            c4r.send: ({},)
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
        ds_sensors.DS18b20.read = self.sensorReadingMock

    def restoreSensorReadingMock(self):
        if self.sensorReadingMock is not None:
            self.sensorReadingMock.reset_mock()

    def methods_exists(self, methods):
        for m in methods:
            self.assertTrue(inspect.ismethod(m))

    def static_methods_exists(self, methods):
        for m in methods:
            is_instance = isinstance(m, types.FunctionType)
            self.assertTrue(is_instance)

    def testDefauls(self):
        self.assertIsNone(lib.device_token)

    def testStaticMethodsExists(self):
        self.static_methods_exists([
            lib.set_device_token,
            lib.register,
            lib.broker_message_handler,
            lib.run_handler,
            lib.read_variables,
            lib.send,
            lib.send_system_info,
        ])

    def testSetApiKey(self):
        self.assertIsNone(lib.device_token)
        lib.set_device_token(device_token)
        self.assertEqual(lib.device_token, device_token)

    def testBindIsHandler(self):
        var1 = {
            'title': 'valid',
            'bind': MockHandler.empty
        }
        var2 = {
            'title': 'invalid',
            'bind': {'address': 'abc'}
        }
        self.assertFalse(helpers.bind_is_handler(None))
        self.assertTrue(helpers.bind_is_handler(var1['bind']))
        self.assertFalse(helpers.bind_is_handler(var2['bind']))

    @patch('c4r.lib.read_sensor')
    def testReadVariables(self, read_sensor_mock):
        print read_sensor_mock
        variables = {'First': {}, 'Last': {}}
        lib.read_variables(variables)
        self.assertEqual(read_sensor_mock.call_count, 2)

    # @staticmethod
    # @patch('c4r.lib.read_cpu')
    # def testReadSystemOnlyWithCpu(mock):
    #     cpuObj = CpuTemperature()
    #     variables = {
    #         'any': {'title': 'abc'},
    #         'CPU': {'title': 'cpu_temp', 'bind': cpuObj},
    #         'noCPU': {'title': 'no_bind'}
    #     }
    #     lib.read_system(variables)
    #     mock.assert_called_with({'title': 'cpu_temp', 'bind': cpuObj})

    # @patch.object(CpuTemperature, 'read')

    def testReadCpuVariable(self):
        cpu_temp = CpuTemperature()
        cpu_temp.read = MagicMock(return_value=36.6)

        cpu_var = {'title': 'cpu_temp', 'bind': cpu_temp}
        self.assertFalse('value' in cpu_var)
        lib.read_variables({'CPU': cpu_var})
        self.assertEqual(cpu_var.get('value'), 36.6)

    def testReadDS18B20Variable(self):
        sensor = ds_sensors.DS18b20('10-000802824e58')
        sensor.read = MagicMock(return_value=22.4)

        var = {'title': 'temp', 'bind': sensor}
        variables = {'Test': var}
        self.assertFalse('value' in var)
        lib.read_variables(variables)
        self.assertEqual(var.get('value'), 22.4)

    @patch.object(MqttTransport, 'send_stream')
    def testSendingVariables(self, mock):
        variables = {'First': {}, 'Last': {}}
        lib.send(variables)
        self.assertEqual(mock.call_count, 1)

    @patch.object(MqttTransport, 'send_stream')
    def testSkipSendingVariables(self, mock):
        variables = {}
        lib.send(variables)
        self.assertFalse(mock.called)


class TestNetworkInfo(unittest.TestCase):
    @patch.object(NetworkInfo, 'read')
    def testGetNetworkInfo(self, mock):
        netObj = NetworkInfo()
        netObj.read()
        self.assertIsNone(netObj.addr)
        self.assertIsNone(netObj.host)


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
        lib.set_device_token(device_token)

    def tearDown(self):
        lib.set_device_token(None)

        # def testSendReceive(self):
        #     variables = {
        #         'temp1': {
        #             'title': '123',
        #             'value': 22.4,
        #             'bind': {'type': 'ds18b20', 'address': '10-000802824e58'}
        #         }
        #     }
        #     self.setUpResponse(self.post, variables, 201)
        #     json = lib.send_receive(variables)
        #     self.assertEqual(json, variables)

        # def testRaiseExceptionOnUnAuthStreamPostRequest(self):
        #     self.setUpPOSTStatus(401)
        #     with self.assertRaises(errors.AuthenticationError):
        #         lib.send_receive({})


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
        obj = CpuTemperature()
        variables = {
            'CPU': {'title': 'cpu_temp', 'bind': obj},
            'NoCPU': {'title': 'no_cpu', 'bind': None}
        }
        self.assertTrue(helpers.bind_is_instance_of(variables['CPU'], CpuTemperature))
        self.assertFalse(helpers.bind_is_instance_of(variables['CPU'], MagicMock))
        self.assertFalse(helpers.bind_is_instance_of(variables['NoCPU'], CpuTemperature))

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
        result = helpers.format_message_topic('test-api-key')
        self.assertEqual(result, 'iot-hub/messages/test-api-key')

    def testFormatSubscriptionTopic(self):
        result = helpers.format_subscription_topic('ledOn')
        self.assertEqual(result, 'iot-hub/commands/ledOn')

    def testIsTokenValid(self):
        self.assertFalse(helpers.is_token_valid('sosmaltokenlength'))
        # deny symbols and 0lIO
        self.assertFalse(helpers.is_token_valid('=3ZQ9NJFcMEK3TWEebnpwUknvB'))
        self.assertFalse(helpers.is_token_valid('-3ZQ9NJFcMEK3TWEebnpwUknvB'))
        self.assertFalse(helpers.is_token_valid('03ZQ9NJFcMEK3TWEebnpwUknv'))
        self.assertFalse(helpers.is_token_valid('l3ZQ9NJFcMEK3TWEebnpwUknv'))
        self.assertFalse(helpers.is_token_valid('I3ZQ9NJFcMEK3TWEebnpwUknv'))
        self.assertFalse(helpers.is_token_valid('O3ZQ9NJFcMEK3TWEebnpwUknv'))

        self.assertTrue(helpers.is_token_valid('3ZQ9NJFcMEK3TWEebnpwUknvB'))

    def testWrapMessages(self):
        payload = {'some': 'thing', 'int': 123}
        result = helpers.wrap_message('my-type', payload)

        self.assertEqual(result['type'], 'my-type')
        self.assertEqual(result['payload'], payload)

    def testSetVariableBoolValue(self):
        variables = {
            'BoolVar': {'type': 'bool', 'value': False},
            'IntVar': {'type': 'numeric', 'value': 0}
        }
        bool_var = variables['BoolVar']
        helpers.set_bool_variable_value(bool_var, '123')
        self.assertEquals(bool_var['value'], True)
        self.assertIsInstance(bool_var['value'], bool)
        self.assertNotIsInstance(bool_var['value'], basestring)

        int_var = variables['IntVar']
        helpers.set_bool_variable_value(int_var, '123')
        self.assertEquals(int_var['value'], '123')
        self.assertNotIsInstance(int_var['value'], bool)
        self.assertIsInstance(int_var['value'], basestring)


class TestDs18b20Sensors(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def setUpSensor(self, address, content):
        self.fs.CreateFile(os.path.join(W1_DEVICES, address, 'w1_slave'), contents=content)

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)

    def testCreateSensorInfo(self):
        sensor = ds_sensors.create_sensor_info('abc')
        self.assertEqual(sensor, {'address': 'abc'})

    def testFindDSSensors(self):
        self.setUpSensors()
        sensors = ds_sensors.DS18b20.find_all()
        self.assertTrue(len(sensors) > 0)
        self.assertIsInstance(sensors[0], ds_sensors.DS18b20)
        self.assertEqual(sensors[0].address, '10-000802824e58')
        self.assertIsInstance(sensors[1], ds_sensors.DS18b20)
        self.assertEqual(sensors[1].address, '28-000802824e58')


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

        mqtt_listener.MqttListener.emit_event('test42')
        self.assertEqual(self.call_args[0], 'test42')

        self.call_args = None
        c4r.on_broker_message -= self.messageHandler
        mqtt_listener.MqttListener.emit_event('other')
        self.assertEqual(self.call_args, None)

    def messageHandler(self, *args):
        self.call_args = args


class ErrorMessages(unittest.TestCase):
    def testGetErrorMessage(self):
        m = c4r.get_error_message(KeyboardInterrupt('test_key_err'))
        self.assertEqual(m, 'Interrupted')
        m = c4r.get_error_message(c4r.errors.InvalidTokenError('abc'))
        self.assertEqual(m, 'API key abc is incorrect. Please verify it.')
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
