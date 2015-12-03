#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import types
import unittest
import os  # should be imported before fake_filesystem_unittest
import c4r
from c4r.lib import Daemon
from c4r import ds18b20 as ds_sensors
from c4r.ds18b20 import W1_DEVICES
from c4r import helpers
import fake_filesystem_unittest
from mock import patch
from mock import MagicMock


device_token = '000000000000000000000001'

sensor_10 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=22250'

sensor_28 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=28250'


class TestApi(unittest.TestCase):
    @patch('c4r.lib.read_persistent')
    def testReadPersistent(self, mock):
        input = {'A': 1}
        c4r.read_persistent(input)
        mock.assert_called_once_with(input)

    @patch('c4r.ds18b20.find_all')
    def testFindDSSensors(self, mock):
        c4r.find_ds_sensors()
        self.assertTrue(mock.called)

class TestDaemon(unittest.TestCase):
    sensorReadingMock = None

    def setUp(self):
        self.lib = Daemon()
        self.assertIsNotNone(self.lib)

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
        self.assertIsNone(self.lib.token)

    def testMethodsExists(self):
        methods = [
            self.lib.set_device_token,
            self.lib.run_handler
        ]
        self.methods_exists(methods)

    def testStaticMethodsExists(self):
        self.static_methods_exists([
            self.lib.find_ds_sensors,
            self.lib.create_ds18b20_sensor,
            self.lib.read_persistent,
            self.lib.send_receive
        ])

    def testSetDeviceToken(self):
        self.assertIsNone(self.lib.token)
        self.lib.set_device_token(device_token)
        self.assertEqual(self.lib.token, device_token)

    def testHandlerExists(self):
        var1 = {
            'title': 'valid',
            'bind': MockHandler.empty
        }
        var2 = {
            'title': 'invalid',
            'bind': {'address': 'abc'}
        }
        self.assertFalse(self.lib.bind_handler_exists(None))
        self.assertFalse(self.lib.bind_handler_exists(var2))
        self.assertTrue(self.lib.bind_handler_exists(var1))


    @patch('c4r.ds18b20.read')
    def testReadPersistent(self, mock):
        addr = '10-000802824e58'
        var = {
            'title': 'temp',
            'bind': {
                'type': 'ds18b20',
                'address': addr
            }
        }
        input = {"Var1": var}

        self.lib.read_persistent(input)
        mock.assert_called_with(addr)

    def testUpdateVariableValueOnRead(self):
        addr = '10-000802824e58'
        var = {
            'title': 'temp',
            'bind': {'type': 'ds18b20', 'address': addr}
        }
        input = {'Test': var}

        self.setUpSensorReading(22.4)

        self.lib.read_persistent(input)
        self.assertEqual(var['value'], 22.4)

    def testCollectReadings(self):
        variables = {
            'temp1': {'title': '123', 'value': 22.4, 'bind': {'type': 'ds18b20'}},
            'some': {'title': '456', 'bind': {'type': 'unknown'}},
            'temp2': {'title': '456', 'bind': {'type': 'ds18b20'}}
        }
        readings = self.lib.collect_readings(variables)
        expected = {'temp2': None, 'temp1': 22.4}
        self.assertEqual(readings, expected)


        # @patch('c4r.daemon.Daemon.run_handler')
        # def testProcessVariables(self, mock):
        # addr = '10-000802824e58'
        # temp = {
        # 'address': addr,
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
        self.lib = Daemon()
        self.assertIsNotNone(self.lib)

    def setUpSensor(self, address, content):
        self.fs.CreateFile(os.path.join(W1_DEVICES, address, 'w1_slave'), contents=content)

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)

    def testCreate_ds18b20_sensor(self):
        sensor = self.lib.create_ds18b20_sensor('abc')
        self.assertEqual(sensor, {'address': 'abc', 'type': 'ds18b20'})

    def testFindDSSensors(self):
        self.setUpSensors()
        sensors = self.lib.find_ds_sensors()
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


def main():
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)


if __name__ == '__main__':
    main()
