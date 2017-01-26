# -*- coding: utf-8 -*-

import unittest
import pyfakefs.fake_filesystem_unittest as ffut

from examples import ds18b20
from examples import rpi

sensor_10 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=22250'

sensor_28 = \
    '2d 00 4d 46 ff ff 08 10 fe : crc=fe YES' '\n' \
    '2d 00 4d 46 ff ff 08 10 fe : t=28250'


class TestDs18b20Sensors(ffut.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.setUpSensors()

    def setUpSensors(self):
        self.setUpSensor('10-000802824e58', sensor_10)
        self.setUpSensor('28-000802824e58', sensor_28)

    def setUpSensor(self, address, content):
        self.fs.CreateFile(
            '/sys/bus/w1/devices/{0}/w1_slave'.format(address),
            contents=content
        )

    def testFindDSSensors(self):
        sensors = ds18b20.DS18b20.find_all()
        self.assertEqual(len(sensors), 2)
        self.assertEqual(sensors[0].address, '10-000802824e58')
        self.assertEqual(sensors[1].address, '28-000802824e58')

    def testRead(self):
        sensor = ds18b20.DS18b20('28-000802824e58')
        result = sensor.read()
        self.assertEqual(result, 28.250)

    def testRaisesExceptionOnInvalidAddress(self):
        with self.assertRaises(ds18b20.InvalidW1Address):
            ds18b20.DS18b20('invalid address')


class TestRpi(unittest.TestCase):

    def testHostName(self):
        self.assertIsNotNone(rpi.hostname)

    def testCpuTemp(self):
        self.assertIsNotNone(rpi.cpu_temp)

    def testOSName(self):
        self.assertIsNotNone(rpi.osname)

    def testIPAddress(self):
        self.assertIsNotNone(rpi.ip_address)


if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))
