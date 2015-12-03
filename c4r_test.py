#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import types
import unittest
import os  # should be imported before fake_filesystem_unittest
import c4r
from c4r.daemon import Daemon
from c4r.ds18b20 import W1_DEVICES
from c4r import helpers
import fake_filesystem_unittest
from mock import patch

device_token = '000000000000000000000001'

sensor_10 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=22250'

sensor_28 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=28250'


class TestApi(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def setUpSensor(self, address, content):
        self.fs.CreateFile(os.path.join(W1_DEVICES, address, 'w1_slave'), contents=content)

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)

    def testReadPersistence(self):
        c4r.read_persistence([])
        self.assertTrue(1)

    def testFindDSSensors(self):
        self.setUpSensors()
        sensors = c4r.find_ds_sensors()
        self.assertTrue(len(sensors) > 0)
        expected = [
            {'address': '10-000802824e58', 'type': 'ds18b20'},
            {'address': '28-000802824e58', 'type': 'ds18b20'}
        ]
        self.assertEqual(sensors, expected)


class TestDaemon(unittest.TestCase):
    def setUp(self):
        self.daemon = Daemon()
        self.assertIsNotNone(self.daemon)

    def methods_exists(self, methods):
        for m in methods:
            self.assertTrue(inspect.ismethod(m))

    def static_methods_exists(self, methods):
        for m in methods:
            isInstance = isinstance(m, types.FunctionType)
            self.assertTrue(isInstance)

    def testDefauls(self):
        self.assertIsNone(self.daemon.token)

    def testMethodsExists(self):
        methods = [
            self.daemon.set_device_token,
            self.daemon.register_variable_handler,
            self.daemon.find_ds_sensors,
            self.daemon.read_persistence,
            self.daemon.run_handler
        ]
        self.methods_exists(methods)

    def testStaticMethodsExists(self):
        self.static_methods_exists([
            self.daemon.create_ds18b20_sensor,
            self.daemon.read_persistent
        ])

    def testSetDeviceToken(self):
        self.assertIsNone(self.daemon.token)
        self.daemon.set_device_token(device_token)
        self.assertEqual(self.daemon.token, device_token)

    @staticmethod
    def _mockVariableHandler(var):
        var['value'] = var['value'] + 1

    @staticmethod
    def _mockHandler(var):
        pass

    def testRegisterVariableHandler(self):
        self.assertEqual(self.daemon.bind_handlers, {})
        self.daemon.register_variable_handler('test', self._mockVariableHandler)

        registered = self.daemon.bind_handlers
        self.assertEqual(len(registered), 1)
        self.assertEqual(registered.keys(), ['test'])
        self.assertEqual(registered.values(), [self._mockVariableHandler])

    def testDoubleRegisterVariableHandler(self):
        self.assertEqual(self.daemon.bind_handlers, {})
        self.daemon.register_variable_handler('test', self._mockVariableHandler)
        self.daemon.register_variable_handler('test', self._mockVariableHandler)

        registered = self.daemon.bind_handlers
        self.assertEqual(len(registered), 1)

    def testSameKeyRegisterVariableHandler(self):
        self.assertEqual(self.daemon.bind_handlers, {})
        self.daemon.register_variable_handler('test', self._mockVariableHandler)
        self.daemon.register_variable_handler('test', self._mockHandler)

        registered = self.daemon.bind_handlers
        self.assertEqual(len(registered), 1)
        self.assertEqual(registered.keys(), ['test'])
        self.assertEqual(registered.values(), [self._mockHandler])

    def testReadPersistence(self):
        temp = {
            'title': 'Temp sensor reading',
            'type': 'numeric',
            'bind': 'onewire',
            'address': '10-000802824e58',
            'value': 0
        }
        self.assertEqual(temp['value'], 0)
        self.daemon.read_persistent(temp, self._mockVariableHandler)
        self.assertNotEqual(temp['value'], 0)

    def testHandlerExists(self):
        self.assertFalse(self.daemon.handler_exists(None))
        self.assertFalse(self.daemon.handler_exists('some'))

        self.daemon.register_variable_handler('first', self._mockHandler)
        self.assertTrue(self.daemon.handler_exists('first'))
        self.assertFalse(self.daemon.handler_exists('other'))


    @patch('c4r.ds18b20.read')
    def testReadPersistence(self, mock):
        addr = '10-000802824e58'
        var  = {
            'title': 'temp',
            'bind': {
                'type': 'ds18b20',
                'address': addr
            }
        }
        self.daemon.read_persistence([var])
        mock.assert_called_with(addr)

    # @patch('c4r.daemon.Daemon.run_handler')
    # def testProcessVariables(self, mock):
    #     addr = '10-000802824e58'
    #     temp = {
    #         'address': addr,
    #         'value': 22
    #     }
    #     self.daemon.register_variable_handler(addr, self._mockHandler)
    #
    #     self.daemon.process_variables([temp])
    #     mock.assert_called_with(addr)


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
        actual = helpers.extract_variable_bind_attr(var, 'address')
        self.assertEqual(actual, addr)


class TestDs18b20Sensors(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.daemon = Daemon()
        self.assertIsNotNone(self.daemon)

    def setUpSensor(self, address, content):
        self.fs.CreateFile(os.path.join(W1_DEVICES, address, 'w1_slave'), contents=content)

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)

    def testCreate_ds18b20_sensor(self):
        sensor = self.daemon.create_ds18b20_sensor('abc')
        self.assertEqual(sensor, {'address': 'abc', 'type': 'ds18b20'})

    def testFindDSSensors(self):
        self.setUpSensors()
        sensors = self.daemon.find_ds_sensors()
        self.assertTrue(len(sensors) > 0)
        expected = [
            {'address': '10-000802824e58', 'type': 'ds18b20'},
            {'address': '28-000802824e58', 'type': 'ds18b20'}
        ]
        self.assertEqual(sensors, expected)


def main():
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)


if __name__ == '__main__':
    main()
