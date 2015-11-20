#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os  # should be imported before fake_filesystem_unittest
import re
import shutil
import subprocess
import json
from collections import namedtuple
import unittest

import datetime
import fake_filesystem_unittest
from mock import MagicMock
from mock import patch
from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner
from requests import RequestException

import cloud4rpi
from cloud4rpi.rpi_daemon import RpiDaemon, find_sensors, read_sensor
from cloud4rpi.helpers import REQUEST_TIMEOUT_SECONDS
from cloud4rpi.server_device import ServerDevice
import cloud4rpi.errors as errors
from settings_vendor import baseApiUrl, config_file, state_file
from sensors import cpu
from sensors.ds18b20 import W1_DEVICES


sensor_10 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=22250'

sensor_22 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=25250'

sensor_28 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=28250'

sensor_no_temp = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : blabla=22250'

device_token = '000000000000000000000001'
scan_interval_seconds = 5
actuators = [{'name': 'LED on pin12', 'address': 'pin12', 'parameters': [{'default': 0}]}]
variables = [{'name': 'temperature', 'type': 'number', 'value': 20}]
TestConfig = namedtuple('object', 'DeviceToken scanIntervalSeconds Actuators Variables')
test_config = TestConfig(device_token, scan_interval_seconds, actuators, variables)
saved_config = {
    '_id': '111111111111111111111111',
    'type': 'Raspberry PI',
    'name': 'test',
    'userId': '222222222222222222222222',
    'state': 1,
    'token': '000000000000000000000001',
    'sensors': [
        {
            '_id': '000000000000000000000000',
            'name': '10-000802824e58',
            'address': '10-000802824e58'
        },
        {
            '_id': '000000000000000000000001',
            'name': '22-000802824e58',
            'address': '22-000802824e58'
        },
        {
            '_id': '000000000000000000000002',
            'name': '28-000802824e58',
            'address': '28-000802824e58'
        }
    ],
    'actuators': actuators,
    'variables': variables
}
saved_state = {
    'configuration': {
        'actuators': {'000000000000000000000010': 42},
        'variables': {'000000000000000000000001': 43}
    }
}


def create_device():
    return {
        'name': 'Test Device',
        'sensors': [
            {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
            {'_id': '000000000000000000000001', 'address': '22-000802824e58'},
            {'_id': '000000000000000000000002', 'address': '28-000802824e58'}
        ],
        'actuators': [
            {
                '_id': '000000000000000000000010', 'address': 'test', 'name': 'test',
                'parameters': [
                    {'_id': '000000000000000000000100', 'name': 'param1', 'value': 42},
                    {'_id': '000000000000000000000100', 'name': 'param2', 'value': 'value2'}
                ]
            }
        ],
        'variables': []
    }


def create_other_device():
    return {
        'name': 'Test Device',
        'sensors': [
            {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
            {'_id': '000000000000000000000002', 'address': '28-000802824e58'}
        ],
        'actuators': [],
        'variables': []
    }


def create_devices_without_sensors():
    return {
        'name': 'Test Device',
        'sensors': [],
        'actuators': [],
        'variables': []
    }


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

    def setUpSensor(self, address, content):
        self.fs.CreateFile(os.path.join(W1_DEVICES, address, 'w1_slave'), contents=content)

    def setUpBogusSensor(self, address, content):
        self.fs.CreateFile(os.path.join(W1_DEVICES, address, 'bogus_readings_source'), contents=content)

    @staticmethod
    def removeSensor(address):
        shutil.rmtree(os.path.join(W1_DEVICES, address))

    @staticmethod
    def listW1Devices():
        return os.listdir(W1_DEVICES)


class TestEndToEnd(TestFileSystemAndRequests):
    def setUp(self):
        super(TestEndToEnd, self).setUp()
        self.setUpSensors()
        self.setUpNow()
        self.setUpShellOutput()
        self.createTestData()
        self.daemon = RpiDaemon(test_config)
        self.setUpDefaultResponses()

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)
        self.setUpSensor('22-000802824e58', sensor_22)
        self.setUpSensor('qw-sasasasasasa', 'garbage garbage garbage')
        self.setUpBogusSensor('22-000000000000', 'I look just like a real sensor, but I\'m not')

    def setUpNoSensors(self):
        for address in self.listW1Devices():
            self.removeSensor(address)

    def setUpDefaultResponses(self):
        self.setUpGET(self.DEVICE)
        self.setUpPUT(self.DEVICE)
        self.setUpPOSTStatus(201)

    def createTestData(self):
        self.DEVICE = create_device()
        self.OTHER_DEVICE = create_other_device()
        self.DEVICE_WITHOUT_SENSORS = create_devices_without_sensors()

    def setUpNow(self):
        self.now = self.startPatching('datetime.datetime.utcnow')
        self.now.return_value = datetime.datetime(2015, 7, 3, 11, 43, 47, 197339)

    def setUpShellOutput(self):
        def side_effect(*args, **kwargs):  # pylint: disable=W0613
            if args[0] == 'DummyCpuAddress':  # cloud4rpi.CPU_USAGE_CMD:
                return '%Cpu(s):\x1b(B\x1b[m\x1b[39;49m\x1b[1m  2.0 \x1b(B\x1b[m\x1b[39;49mus\n' \
                       '%Cpu(s):\x1b(B\x1b[m\x1b[39;49m\x1b[1m  4.2 \x1b(B\x1b[m\x1b[39;49mus\n'
            else:
                return "temp=37.9'C\n"

        self.check_output = self.startPatching('subprocess.check_output')
        self.check_output.side_effect = side_effect

    def setUpShellError(self):
        self.check_output.side_effect = subprocess.CalledProcessError(1, 'any cmd')

    def tick(self):
        self.daemon.prepare()
        self.daemon.send_device_config()
        self.daemon.tick()

    def testGetDevice(self):
        self.daemon.prepare()
        self.daemon.send_device_config()

        self.get.assert_called_once_with(baseApiUrl + '/devices/000000000000000000000001/',
                                         headers={'api_key': '000000000000000000000001'},
                                         timeout=REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(self.daemon.me.dump(), self.DEVICE)

    def testLoadSavedDeviceConfig(self):
        self.fs.CreateFile(os.path.join(config_file), contents=json.dumps(saved_config))

        self.daemon.prepare()
        self.daemon.send_device_config()

        self.put.assert_called_once_with(baseApiUrl + '/devices/000000000000000000000001/',
                                         headers={'api_key': '000000000000000000000001'},
                                         json=saved_config,
                                         timeout=REQUEST_TIMEOUT_SECONDS)

    @patch('cloud4rpi.rpi_daemon.parent_conn')
    def testLoadSavedDeviceState(self, parent_conn):
        self.fs.CreateFile(os.path.join(state_file), contents=json.dumps(saved_state))

        self.daemon.prepare()
        for act_id, act_state in saved_state['configuration']['actuators'].iteritems():
            parent_conn.send.assert_any_call({'id': act_id, 'state': act_state})
        for act_id, act_state in saved_state['configuration']['variables'].iteritems():
            parent_conn.send.assert_any_call({'id': act_id, 'value': act_state})

    def testCreateNewlyFoundSensorsOnExistingDevice(self):
        self.setUpGET(self.OTHER_DEVICE)

        self.daemon.prepare()
        self.daemon.send_device_config()

        expected_device = {
            'name': 'Test Device',
            'type': 'Raspberry PI',
            'sensors': [
                {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
                {'_id': '000000000000000000000002', 'address': '28-000802824e58'},
                {'name': '22-000802824e58', 'address': '22-000802824e58'},
            ],
            'actuators': test_config.Actuators,
            'variables': test_config.Variables
        }
        self.put.assert_called_once_with(baseApiUrl + '/devices/000000000000000000000001/',
                                         headers={'api_key': '000000000000000000000001'},
                                         json=expected_device,
                                         timeout=REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(self.daemon.me.dump(), self.DEVICE)

    def testConnectNewDevice(self):
        self.setUpGET(self.DEVICE_WITHOUT_SENSORS)

        self.daemon.prepare()
        self.daemon.send_device_config()

        expected_device = {
            'name': 'Test Device',
            'type': 'Raspberry PI',
            'sensors': [
                {'name': '10-000802824e58', 'address': '10-000802824e58'},
                {'name': '22-000802824e58', 'address': '22-000802824e58'},
                {'name': '28-000802824e58', 'address': '28-000802824e58'},
            ],
            'actuators': test_config.Actuators,
            'variables': test_config.Variables
        }
        self.put.assert_called_once_with(baseApiUrl + '/devices/000000000000000000000001/',
                                         headers={'api_key': '000000000000000000000001'},
                                         json=expected_device,
                                         timeout=REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(self.daemon.me.dump(), self.DEVICE)

    def testStreamPost(self):
        self.tick()

        expected_stream = {
            'ts': '2015-07-03T11:43:47.197339',
            'payload': {
                '000000000000000000000000': 22.25,
                '000000000000000000000001': 25.25,
                '000000000000000000000002': 28.25
            }
        }
        self.post.assert_any_call(baseApiUrl + '/devices/000000000000000000000001/streams/',
                                  headers={'api_key': '000000000000000000000001'},
                                  json=expected_stream,
                                  timeout=REQUEST_TIMEOUT_SECONDS)

    def testSystemParametersSending(self):
        self.tick()

        expected_parameters = {
            # 'cpuUsage': 4.2,
            'cpuTemperature': 37.9
        }
        self.post.assert_any_call(baseApiUrl + '/devices/000000000000000000000001/params/',
                                  headers={'api_key': '000000000000000000000001'},
                                  json=expected_parameters,
                                  timeout=REQUEST_TIMEOUT_SECONDS)
        # self.check_output.assert_any_call(cloud4rpi.CPU_USAGE_CMD, shell=True)
        self.check_output.assert_any_call(cpu.CPU_TEMPERATURE_CMD, shell=True)

    def testRaiseExceptionOnUnAuthStreamPostRequest(self):
        self.setUpPOSTStatus(401)

        with self.assertRaises(errors.AuthenticationError):
            self.tick()

    def testDoNotSendSystemParametersOnTheirRetrievingError(self):
        self.setUpShellError()

        self.tick()

        self.assertEqual(1, self.post.call_count)

    def testRaiseExceptionOnUnAuthDeviceGetRequest(self):
        self.setUpGETStatus(401)

        with self.assertRaises(errors.AuthenticationError):
            self.tick()

    def testRaisesExceptionOnUnAuthDevicePutRequest(self):
        self.setUpGET(self.DEVICE_WITHOUT_SENSORS)
        self.setUpPUTStatus(401)

        with self.assertRaises(errors.AuthenticationError):
            self.tick()

    def testSkipFailedStreams(self):
        self.post.side_effect = RequestException

        self.tick()

    def testSkipFailedSystemParameters(self):
        self.post.side_effect = [MagicMock(), RequestException]

        self.tick()

    #@timeout(1)
    def testRaisesExceptionWhenThereAreNoSensors(self):
        self.setUpNoSensors()

        with self.assertRaises(errors.NoSensorsError):
            self.daemon.run()

    def testReadSensors(self):
        self.tick()

        readings = self.daemon.read_sensors()
        self.assertListEqual(sorted(readings), [
            ('10-000802824e58', 22.25),
            ('22-000802824e58', 25.25),
            ('28-000802824e58', 28.25)
        ])

    @patch('sensors.ds18b20.read')
    def testReadSensorsWithException(self, m_read):
        m_read.side_effect = Exception('Boom!')

        self.daemon.prepare_sensors()

        readings = self.daemon.read_sensors()
        self.assertListEqual(sorted(readings), [])

    def testReadSensorsWithNoneReading(self):
        self.removeSensor('10-000802824e58')
        self.removeSensor('22-000802824e58')
        self.removeSensor('28-000802824e58')

        self.setUpSensor('10-000802824e58', sensor_no_temp)
        self.setUpSensor('28-000802824e58', sensor_no_temp)


        self.daemon.prepare_sensors()

        readings = self.daemon.read_sensors()

        self.assertListEqual(sorted(readings), [
            ('10-000802824e58', None),
            ('28-000802824e58', None)
        ])


class TestServerDevice(unittest.TestCase):
    def testSensorAddrs(self):
        sensors = ServerDevice(create_device()).extension_addrs()
        self.assertListEqual(sorted(sensors), ['10-000802824e58', '22-000802824e58', '28-000802824e58', 'test'])

    def testWhatsNew(self):
        device = ServerDevice(create_other_device())
        new_sensors = device.whats_new(['10-000802824e58', '22-000802824e58', '28-000802824e58'])
        self.assertSetEqual(new_sensors, {'22-000802824e58'})

    def testMapSensors(self):
        device = ServerDevice(create_device())
        readings = [
            ('10-000802824e58', 22.25),
            ('22-000802824e58', 25.25),
            ('28-000802824e58', 28.25)
        ]
        payload = device.map_extensions(readings)
        self.assertDictEqual(payload, {
            '000000000000000000000000': 22.25,
            '000000000000000000000001': 25.25,
            '000000000000000000000002': 28.25
        })

    def testSetType(self):
        device = ServerDevice(create_device())
        device.set_type('Raspberry PI')
        self.assertEqual(device.dump()['type'], 'Raspberry PI')


class TestDeviceWithoutSensors(unittest.TestCase):
    def setUp(self):
        self.device = ServerDevice(create_devices_without_sensors())

    def testSensorAddrs(self):
        self.assertEqual(0, len(self.device.extension_addrs()))

    def testWhatsNew(self):
        new_sensors = self.device.whats_new(['10-000802824e58', '22-000802824e58', '28-000802824e58'])
        self.assertSetEqual(new_sensors, {'10-000802824e58', '22-000802824e58', '28-000802824e58'})

    def testMapSensors(self):
        readings = [
            ('10-000802824e58', 22.25),
            ('22-000802824e58', 25.25),
            ('28-000802824e58', 28.25)
        ]
        payload = self.device.map_extensions(readings)
        self.assertEqual(0, len(payload))


class TestUtils(TestFileSystemAndRequests):
    def setUp(self):
        super(TestUtils, self).setUp()
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)
        self.setUpSensor('22-000802824e58', sensor_22)
        self.setUpSensor('qw-sasasasasasa', 'garbage garbage garbage')

    def testFindSensors(self):
        sensors = find_sensors()
        self.assertListEqual(sorted(sensors), [
            '10-000802824e58',
            '22-000802824e58',
            '28-000802824e58',
        ])

    def testReadSensor(self):
        data = read_sensor('22-000802824e58')
        self.assertEqual(data, ('22-000802824e58', 25.250))

    # def testCpuUsageCmd(self):
    #     self.assertEqual("top -n2 -d.1 | awk -F ',' '/Cpu\(s\):/ {print $1}'", cloud4rpi.CPU_USAGE_CMD)

    def testCpuTemperatureCmd(self):
        self.assertEqual("vcgencmd measure_temp", cpu.CPU_TEMPERATURE_CMD)

    def testW1DevicesPath(self):
        self.assertEqual('/sys/bus/w1/devices/', W1_DEVICES)

    def testLogFilePath(self):
        self.assertEqual('/var/log/cloud4rpi.log', cloud4rpi.LOG_FILE_PATH)

    def testRequestTimeout(self):
        self.assertEqual(3 * 60 + 0.05, REQUEST_TIMEOUT_SECONDS)


class TestFileLineSeparator(fake_filesystem_unittest.TestCase):
    @staticmethod
    def extractFiles(filesPath):
        files = os.listdir(filesPath)
        return [x for x in files if x.endswith(('.txt', '.py', '.sh', '.tmpl'))]

    def checkFiles(self, filesPath):
        CR = re.compile('\r')
        files = self.extractFiles(filesPath)
        for fileName in files:
            with open(fileName) as f:
                print fileName
                for line in f:
                    self.assertFalse(CR.match(line))

    def testUnixLineEnding(self):
        self.checkFiles(os.curdir)


def main():
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)


if __name__ == '__main__':
    main()
