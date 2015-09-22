#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os  # should be imported before fake_filesystem_unittest
import re
import shutil
import datetime
import subprocess

import unittest
import fake_filesystem_unittest

from timeout_decorator import timeout
from mock import MagicMock
from mock import patch

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner

from requests import RequestException

import cloud4rpid
from cloud4rpid import RpiDaemon
from cloud4rpid import W1_DEVICES
from sensors import cpu

sensor_10 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=22250'

sensor_22 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=25250'

sensor_28 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=28250'


def create_device():
    return {
        'name': 'Test Device',
        'sensors': [
            {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
            {'_id': '000000000000000000000001', 'address': '22-000802824e58'},
            {'_id': '000000000000000000000002', 'address': '28-000802824e58'}
        ]
    }


def create_other_device():
    return {
        'name': 'Test Device',
        'sensors': [
            {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
            {'_id': '000000000000000000000002', 'address': '28-000802824e58'}
        ]
    }


def create_devices_without_sensors():
    return {
        'name': 'Test Device',
        'sensors': []
    }

class TestFileSystemAndRequests(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.patchRequests()

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
        self.daemon = RpiDaemon('000000000000000000000001')
        self.setUpDefaultResponses()

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)
        self.setUpSensor('22-000802824e58', sensor_22)
        self.setUpSensor('qw-sasasasasasa', 'garbage garbage garbage')
        self.setUpBogusSensor('22-000000000000', "I look just like a real sensor, but I'm not")

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
        def side_effect(*args, **kwargs): # pylint: disable=W0613
            if args[0] == 'DummyCpuAddress': #cloud4rpid.CPU_USAGE_CMD:
                return '%Cpu(s):\x1b(B\x1b[m\x1b[39;49m\x1b[1m  2.0 \x1b(B\x1b[m\x1b[39;49mus\n' \
                       '%Cpu(s):\x1b(B\x1b[m\x1b[39;49m\x1b[1m  4.2 \x1b(B\x1b[m\x1b[39;49mus\n'
            else:
                return "temp=37.9'C\n"

        self.check_output = self.startPatching('subprocess.check_output')
        self.check_output.side_effect = side_effect

    def setUpShellError(self):
        self.check_output.side_effect = subprocess.CalledProcessError(1, 'any cmd')

    def tick(self):
        self.daemon.prepare_sensors()
        self.daemon.tick()

    def testGetDevice(self):
        self.daemon.prepare_sensors()

        self.get.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/',
                                         headers={'api_key': '000000000000000000000001'},
                                         timeout=cloud4rpid.REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(self.daemon.me.dump(), self.DEVICE)

    def testCreateNewlyFoundSensorsOnExistingDevice(self):
        self.setUpGET(self.OTHER_DEVICE)

        self.daemon.prepare_sensors()

        expected_device = {
            'name': 'Test Device',
            'type': 'Raspberry PI',
            'sensors': [
                {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
                {'_id': '000000000000000000000002', 'address': '28-000802824e58'},
                {'name': '22-000802824e58', 'address': '22-000802824e58'},
            ]
        }
        self.put.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/',
                                         headers={'api_key': '000000000000000000000001'},
                                         json=expected_device,
                                         timeout=cloud4rpid.REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(self.daemon.me.dump(), self.DEVICE)

    def testConnectNewDevice(self):
        self.setUpGET(self.DEVICE_WITHOUT_SENSORS)

        self.daemon.prepare_sensors()

        expected_device = {
            'name': 'Test Device',
            'type': 'Raspberry PI',
            'sensors': [
                {'name': '10-000802824e58', 'address': '10-000802824e58'},
                {'name': '22-000802824e58', 'address': '22-000802824e58'},
                {'name': '28-000802824e58', 'address': '28-000802824e58'},
            ]
        }
        self.put.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/',
                                         headers={'api_key': '000000000000000000000001'},
                                         json=expected_device,
                                         timeout=cloud4rpid.REQUEST_TIMEOUT_SECONDS)
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
        self.post.assert_any_call('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/streams/',
                                  headers={'api_key': '000000000000000000000001'},
                                  json=expected_stream,
                                  timeout=cloud4rpid.REQUEST_TIMEOUT_SECONDS)

    def testSystemParametersSending(self):
        self.tick()

        expected_parameters = {
            # 'cpuUsage': 4.2,
            'cpuTemperature': 37.9
        }
        self.post.assert_any_call('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/params/',
                                  headers={'api_key': '000000000000000000000001'},
                                  json=expected_parameters,
                                  timeout=cloud4rpid.REQUEST_TIMEOUT_SECONDS)
        # self.check_output.assert_any_call(cloud4rpid.CPU_USAGE_CMD, shell=True)
        self.check_output.assert_any_call(cpu.CPU_TEMPERATURE_CMD, shell=True)

    def testRaiseExceptionOnUnAuthStreamPostRequest(self):
        self.setUpPOSTStatus(401)

        with self.assertRaises(cloud4rpid.AuthenticationError):
            self.tick()

    def testDoNotSendSystemParametersOnTheirRetrievingError(self):
        self.setUpShellError()

        self.tick()

        self.assertEqual(1, self.post.call_count)

    def testRaiseExceptionOnUnAuthDeviceGetRequest(self):
        self.setUpGETStatus(401)

        with self.assertRaises(cloud4rpid.AuthenticationError):
            self.tick()

    def testRaisesExceptionOnUnAuthDevicePutRequest(self):
        self.setUpGET(self.DEVICE_WITHOUT_SENSORS)
        self.setUpPUTStatus(401)

        with self.assertRaises(cloud4rpid.AuthenticationError):
            self.tick()

    def testSkipFailedStreams(self):
        self.post.side_effect = RequestException

        self.tick()

    def testSkipFailedSystemParameters(self):
        self.post.side_effect = [MagicMock(), RequestException]

        self.tick()

    @timeout(1)
    def testRaisesExceptionWhenThereAreNoSensors(self):
        self.setUpNoSensors()

        with self.assertRaises(cloud4rpid.NoSensorsError):
            self.daemon.run()

    def testReadSensors(self):
        self.tick()

        readings = self.daemon.read_sensors()
        self.assertListEqual(sorted(readings), [
            ('10-000802824e58', 22.25),
            ('22-000802824e58', 25.25),
            ('28-000802824e58', 28.25)
        ])


class TestServerDevice(unittest.TestCase):
    def testSensorAddrs(self):
        sensors = cloud4rpid.ServerDevice(create_device()).sensor_addrs()
        self.assertListEqual(sorted(sensors), ['10-000802824e58', '22-000802824e58', '28-000802824e58'])

    def testWhatsNew(self):
        device = cloud4rpid.ServerDevice(create_other_device())
        new_sensors = device.whats_new(['10-000802824e58', '22-000802824e58', '28-000802824e58'])
        self.assertSetEqual(new_sensors, {'22-000802824e58'})

    def testMapSensors(self):
        device = cloud4rpid.ServerDevice(create_device())
        readings = [
            ('10-000802824e58', 22.25),
            ('22-000802824e58', 25.25),
            ('28-000802824e58', 28.25)
        ]
        payload = device.map_sensors(readings)
        self.assertDictEqual(payload, {
            '000000000000000000000000': 22.25,
            '000000000000000000000001': 25.25,
            '000000000000000000000002': 28.25
        })

    def testSetType(self):
        device = cloud4rpid.ServerDevice(create_device())
        device.set_type('Raspberry PI')
        self.assertEqual(device.dump()['type'], 'Raspberry PI')


class TestDeviceWithoutSensors(unittest.TestCase):
    def setUp(self):
        self.device = cloud4rpid.ServerDevice(create_devices_without_sensors())

    def testSensorAddrs(self):
        self.assertEqual(0, len(self.device.sensor_addrs()))

    def testWhatsNew(self):
        new_sensors = self.device.whats_new(['10-000802824e58', '22-000802824e58', '28-000802824e58'])
        self.assertSetEqual(new_sensors, {'10-000802824e58', '22-000802824e58', '28-000802824e58'})

    def testMapSensors(self):
        readings = [
            ('10-000802824e58', 22.25),
            ('22-000802824e58', 25.25),
            ('28-000802824e58', 28.25)
        ]
        payload = self.device.map_sensors(readings)
        self.assertEqual(0, len(payload))


class TestUtils(TestFileSystemAndRequests):
    def setUp(self):
        super(TestUtils, self).setUp()
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)
        self.setUpSensor('22-000802824e58', sensor_22)
        self.setUpSensor('qw-sasasasasasa', 'garbage garbage garbage')

    def testFindSensors(self):
        sensors = cloud4rpid.find_sensors()
        self.assertListEqual(sorted(sensors), [
            '10-000802824e58',
            '22-000802824e58',
            '28-000802824e58',
        ])

    def testReadSensor(self):
        data = cloud4rpid.read_sensor('22-000802824e58')
        self.assertEqual(data, ('22-000802824e58', 25.250))

    # def testCpuUsageCmd(self):
    #     self.assertEqual("top -n2 -d.1 | awk -F ',' '/Cpu\(s\):/ {print $1}'", cloud4rpid.CPU_USAGE_CMD)

    def testCpuTemperatureCmd(self):
        self.assertEqual("vcgencmd measure_temp", cpu.CPU_TEMPERATURE_CMD)

    def testW1DevicesPath(self):
        self.assertEqual('/sys/bus/w1/devices/', cloud4rpid.W1_DEVICES)

    def testLogFilePath(self):
        self.assertEqual('/var/log/cloud4rpid.log', cloud4rpid.LOG_FILE_PATH)

    def testRequestTimeout(self):
        self.assertEqual(3 * 60 + 0.05, cloud4rpid.REQUEST_TIMEOUT_SECONDS)

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


if __name__ == '__main__':
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
