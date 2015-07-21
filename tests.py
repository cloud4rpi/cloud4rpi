import os  # should be imported before fake_filesystem_unittest
import datetime
import subprocess

import unittest
import fake_filesystem_unittest

from mock import MagicMock
from mock import patch

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner

from requests import RequestException

import cloud4rpid

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

    def setUpResponse(self, verb, response):
        r_mock = MagicMock(['json', 'status_code'])
        r_mock.json.return_value = response
        r_mock.status_code = 200
        verb.return_value = r_mock

    def setUpStatusCode(self, verb, code):
        r_mock = MagicMock()
        r_mock.status_code = code
        verb.return_value = r_mock

    def setUpSensor(self, address, content):
        self.fs.CreateFile(os.path.join('/sys/bus/w1/devices/', address, 'w1_slave'), contents=content)

    def setUpBogusSensor(self, address, content):
        self.fs.CreateFile(os.path.join('/sys/bus/w1/devices/', address, 'bogus_readings_source'), contents=content)


class TestEndToEnd(TestFileSystemAndRequests):
    def setUp(self):
        super(TestEndToEnd, self).setUp()
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)
        self.setUpSensor('22-000802824e58', sensor_22)
        self.setUpSensor('qw-sasasasasasa', 'garbage garbage garbage')
        self.setUpBogusSensor('22-000000000000', "I look just like a real sensor, but I'm not")
        self.DEVICE = create_device()
        self.OTHER_DEVICE = create_other_device()
        self.DEVICE_WITHOUT_SENSORS = create_devices_without_sensors()

    def setUpNow(self, now):
        now.return_value = datetime.datetime(2015, 7, 3, 11, 43, 47, 197339)

    def setUpShellOutput(self, shell_func):
        def side_effect(*args, **kwargs):
            if args[0] == cloud4rpid.CPU_USAGE_CMD:
                return '%Cpu(s):\x1b(B\x1b[m\x1b[39;49m\x1b[1m  2.0 \x1b(B\x1b[m\x1b[39;49mus\n' \
                       '%Cpu(s):\x1b(B\x1b[m\x1b[39;49m\x1b[1m  4.2 \x1b(B\x1b[m\x1b[39;49mus\n'
            else:
                return "temp=37.9'C\n"

        shell_func.side_effect = side_effect

    @patch('requests.get')
    def testGetDevice(self, get):
        self.setUpResponse(get, self.DEVICE)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()

        get.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/',
                                    headers={'api_key': '000000000000000000000001'})
        self.assertEqual(daemon.me.dump(), self.DEVICE)

    @patch('requests.put')
    @patch('requests.get')
    def testCreateNewlyFoundSensorsOnExistingDevice(self, get, put):
        self.setUpResponse(get, self.OTHER_DEVICE)
        self.setUpResponse(put, self.DEVICE)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()

        expected_device = {
            'name': 'Test Device',
            'sensors': [
                {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
                {'_id': '000000000000000000000002', 'address': '28-000802824e58'},
                {'name': '22-000802824e58', 'address': '22-000802824e58'},
            ]
        }
        put.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/',
                                    headers={'api_key': '000000000000000000000001'},
                                    json=expected_device)
        self.assertEqual(daemon.me.dump(), self.DEVICE)

    @patch('requests.put')
    @patch('requests.get')
    def testConnectNewDevice(self, get, put):
        self.setUpResponse(get, self.DEVICE_WITHOUT_SENSORS)
        self.setUpResponse(put, self.DEVICE)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000002')
        daemon.prepare_sensors()

        expected_device = {
            'name': 'Test Device',
            'sensors': [
                {'name': '10-000802824e58', 'address': '10-000802824e58'},
                {'name': '22-000802824e58', 'address': '22-000802824e58'},
                {'name': '28-000802824e58', 'address': '28-000802824e58'},
            ]
        }
        put.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000002/',
                                    headers={'api_key': '000000000000000000000002'},
                                    json=expected_device)
        self.assertEqual(daemon.me.dump(), self.DEVICE)

    @patch('subprocess.check_output')
    @patch('datetime.datetime.utcnow')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testStreamPost(self, get, put, post, now, check_output):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)
        self.setUpStatusCode(post, 201)
        self.setUpNow(now)
        self.setUpShellOutput(check_output)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()
        daemon.tick()

        stream = {
            'ts': '2015-07-03T11:43:47.197339',
            'payload': {
                '000000000000000000000000': 22.25,
                '000000000000000000000001': 25.25,
                '000000000000000000000002': 28.25
            }
        }

        post.assert_any_call('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/streams/',
                             headers={'api_key': '000000000000000000000001'},
                             json=stream)

    @patch('subprocess.check_output')
    @patch('datetime.datetime.utcnow')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testSystemParametersSending(self, get, put, post, now, check_output):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)
        self.setUpStatusCode(post, 201)
        self.setUpNow(now)
        self.setUpShellOutput(check_output)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()
        daemon.tick()

        parameters = {
            'cpuUsage': 4.2,
            'cpuTemperature': 37.9
        }

        post.assert_any_call('http://stage.cloud4rpi.io:3000/api/devices/000000000000000000000001/params/',
                             headers={'api_key': '000000000000000000000001'},
                             json=parameters)
        check_output.assert_any_call(cloud4rpid.CPU_USAGE_CMD, shell=True)
        check_output.assert_any_call(cloud4rpid.CPU_TEMPERATURE_CMD, shell=True)

    @patch('datetime.datetime.utcnow')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testRaiseExceptionOnUnAuthStreamPostRequest(self, get, put, post, now):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)
        self.setUpStatusCode(post, 401)
        self.setUpNow(now)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()

        with self.assertRaises(cloud4rpid.AuthenticationError):
            daemon.tick()

    @patch('subprocess.check_output')
    @patch('datetime.datetime.utcnow')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testDontSendSystemParametersOnTheirRetrievingError(self, get, put, post, now, check_output):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)
        self.setUpStatusCode(post, 201)
        self.setUpNow(now)
        check_output.side_effect = subprocess.CalledProcessError(1, 'any cmd')

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()
        daemon.tick()

        self.assertEqual(1, post.call_count)

    @patch('requests.get')
    def testRaiseExceptionOnUnAuthDeviceGetRequest(self, get):
        self.setUpStatusCode(get, 401)
        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')

        with self.assertRaises(cloud4rpid.AuthenticationError):
            daemon.prepare_sensors()

    @patch('requests.put')
    @patch('requests.get')
    def testRaisesExceptionOnUnAuthDevicePutRequest(self, get, put):
        self.setUpResponse(get, self.DEVICE_WITHOUT_SENSORS)
        self.setUpStatusCode(put, 401)
        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')

        with self.assertRaises(cloud4rpid.AuthenticationError):
            daemon.prepare_sensors()

    @patch('subprocess.check_output')
    @patch('datetime.datetime.now')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testSkipFailedStreams(self, get, put, post, now, check_output):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)
        post.side_effect = RequestException
        self.setUpNow(now)
        self.setUpShellOutput(check_output)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()
        daemon.tick()

    @patch('subprocess.check_output')
    @patch('datetime.datetime.now')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testSkipFailedSystemParameters(self, get, put, post, now, check_output):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)
        post.side_effect = [MagicMock(), RequestException]
        self.setUpNow(now)
        self.setUpShellOutput(check_output)

        daemon = cloud4rpid.RpiDaemon('000000000000000000000001')
        daemon.prepare_sensors()
        daemon.tick()


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

    def testReadSensors(self):
        readings = cloud4rpid.read_sensors()
        self.assertListEqual(sorted(readings), [
            ('10-000802824e58', 22.25),
            ('22-000802824e58', 25.25),
            ('28-000802824e58', 28.25)
        ])

    def testCpuUsageCmd(self):
        self.assertEqual("top -n2 -d.1 | awk -F ',' '/Cpu\(s\):/ {print $1}'", cloud4rpid.CPU_USAGE_CMD)

    def testCpuTemperatureCmd(self):
        self.assertEqual("vcgencmd measure_temp", cloud4rpid.CPU_TEMPERATURE_CMD)


if __name__ == '__main__':
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
