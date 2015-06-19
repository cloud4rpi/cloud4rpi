import os
import json

import unittest
import fake_filesystem_unittest

from mock import MagicMock
from mock import patch

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


class TestEndToEnd(fake_filesystem_unittest.TestCase):
    @staticmethod
    def setUpSensor(fs, address, content):
        fs.CreateFile(os.path.join('/sys/bus/w1/devices/', address, 'w1_slave'), contents=content)

    @staticmethod
    def setUpResponse(method_mock, response):
        r_mock = MagicMock(['json', 'status_code'])
        r_mock.json.return_value = response
        method_mock.return_value = r_mock

    def setUpStatusCode(self, post, code):
        r_mock = MagicMock()
        r_mock.status_code = code
        post.return_value = r_mock

    def setUp(self):
        self.setUpPyfakefs()
        self.setUpSensor(self.fs, '10-000802824e58', sensor_10)
        self.setUpSensor(self.fs, '28-000802824e58', sensor_28)
        self.setUpSensor(self.fs, '22-000802824e58', sensor_22)
        self.setUpSensor(self.fs, 'qw-sasasasasasa', 'garbage garbage garbage')
        self.DEVICE = create_device()
        self.OTHER_DEVICE = create_other_device()

    @patch('requests.get')
    def testGetDevice(self, get):
        self.setUpResponse(get, self.DEVICE)

        device = cloud4rpid.get_device('000000000000000000000000')

        get.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/device/000000000000000000000000/')
        self.assertListEqual(sorted(device.sensor_addrs()), ['10-000802824e58', '22-000802824e58', '28-000802824e58'])

    @patch('requests.get')
    def testGetDevice(self, get):
        self.setUpResponse(get, self.DEVICE)

        daemon = cloud4rpid.RpiDaemon()
        daemon.token = '000000000000000000000001'
        daemon.prepare_sensors()

        get.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/device/000000000000000000000001/')

    @patch('requests.put')
    @patch('requests.get')
    def testNewSensorCreation(self, get, put):
        self.setUpResponse(get, self.OTHER_DEVICE)
        self.setUpResponse(put, self.DEVICE)

        daemon = cloud4rpid.RpiDaemon()
        daemon.token = '000000000000000000000001'
        daemon.prepare_sensors()

        device = json.dumps({
            'name': 'Test Device',
            'sensors': [
                {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
                {'_id': '000000000000000000000002', 'address': '28-000802824e58'},
                {'name': '22-000802824e58', 'address': '22-000802824e58'},
            ]
        })
        put.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/device/000000000000000000000001/',
                                    headers={'api_key': '000000000000000000000001'},
                                    data=device)

    @patch('requests.put')
    @patch('requests.get')
    def testNewSensorCreation2(self, get, put):
        self.setUpResponse(get, self.OTHER_DEVICE)
        self.setUpResponse(put, self.DEVICE)

        daemon = cloud4rpid.RpiDaemon()
        daemon.prepare_sensors()

        self.assertEqual(daemon.me.dump(), json.dumps(self.DEVICE))

    @patch('time.time')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testStreamPost(self, get, put, post, time):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)

        time.return_value = 1111111111.1111

        daemon = cloud4rpid.RpiDaemon()
        daemon.token = '000000000000000000000001'
        daemon.prepare_sensors()
        daemon.tick()

        stream = json.dumps({
            'ts': 1111111111,
            'payload': [
                {'000000000000000000000000': 22.25},
                {'000000000000000000000001': 25.25},
                {'000000000000000000000002': 28.25},
            ]
        })

        post.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/device/000000000000000000000001/stream/',
                                     headers={'api_key': '000000000000000000000001'},
                                     data=stream)

    @patch('time.time')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def testRaiseExceptionOnUnAuthStreamPostRequest(self, get, put, post, time):
        self.setUpResponse(get, self.DEVICE)
        self.setUpResponse(put, self.DEVICE)
        self.setUpStatusCode(post, 401)
        time.return_value = 1111111111.1111

        daemon = cloud4rpid.RpiDaemon()
        daemon.token = '000000000000000000000001'
        daemon.prepare_sensors()

        with self.assertRaises(cloud4rpid.AuthenticationError):
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
        self.assertListEqual(payload, [
            {'000000000000000000000000': 22.25},
            {'000000000000000000000001': 25.25},
            {'000000000000000000000002': 28.25},
        ])


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


class TestUtils(fake_filesystem_unittest.TestCase):
    @staticmethod
    def setUpSensor(fs, address, content):
        fs.CreateFile(os.path.join('/sys/bus/w1/devices/', address, 'w1_slave'), contents=content)

    def setUp(self):
        self.setUpPyfakefs()
        self.setUpSensor(self.fs, '10-000802824e58', sensor_10)
        self.setUpSensor(self.fs, '28-000802824e58', sensor_28)
        self.setUpSensor(self.fs, '22-000802824e58', sensor_22)
        self.setUpSensor(self.fs, 'qw-sasasasasasa', 'garbage garbage garbage')

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


if __name__ == '__main__':
    unittest.main()
