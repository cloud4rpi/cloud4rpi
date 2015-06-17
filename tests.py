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


class TestEndToEnd(fake_filesystem_unittest.TestCase):
    @staticmethod
    def setUpSensor(fs, address, content):
        fs.CreateFile(os.path.join('/sys/bus/w1/devices/', address, 'w1_slave'), contents=content)

    @staticmethod
    def setUpResponse(method_mock, response):
        r_mock = MagicMock(['json'])
        r_mock.json.return_value = response
        method_mock.return_value = r_mock

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

        self.assertListEqual(sorted(device.sensor_addrs()), ['10-000802824e58', '22-000802824e58', '28-000802824e58'])

    @patch('requests.put')
    @patch('requests.get')
    def testNewSensorCreation(self, get, put):
        self.setUpResponse(get, self.OTHER_DEVICE)
        self.setUpResponse(put, self.DEVICE)

        daemon = cloud4rpid.RpiDaemon()
        daemon.prepare_sensors()

        device = json.dumps({
            'name': 'Test Device',
            'sensors': [
                {'_id': '000000000000000000000000', 'address': '10-000802824e58'},
                {'_id': '000000000000000000000002', 'address': '28-000802824e58'},
                {'address': '22-000802824e58'},
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

        time.return_value = 11111111111111.1111

        daemon = cloud4rpid.RpiDaemon()
        daemon.prepare_sensors()
        daemon.tick()

        stream = json.dumps({
            'ts': 11111111111111,
            'payload': [
                {'000000000000000000000000': 22.25},
                {'000000000000000000000001': 25.25},
                {'000000000000000000000002': 28.25},
            ]
        })

        post.assert_called_once_with('http://stage.cloud4rpi.io:3000/api/device/000000000000000000000001/stream/',
                                     headers={'api_key': '000000000000000000000001'},
                                     data=stream)


class TestServerDevice(unittest.TestCase):
    def setUp(self):
        self.DEVICE = create_device()
        self.device = cloud4rpid.ServerDevice(self.DEVICE)

    def testSensorAddrs(self):
        sensors = self.device.sensor_addrs()
        self.assertListEqual(sorted(sensors), ['10-000802824e58', '22-000802824e58', '28-000802824e58'])

    def testWhatsNew(self):
        device = cloud4rpid.ServerDevice(create_other_device())
        new_sensors = device.whats_new(['10-000802824e58', '22-000802824e58', '28-000802824e58'])
        self.assertSetEqual(new_sensors, {'22-000802824e58'})


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
