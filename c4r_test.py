#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import unittest
from c4r.daemon import Daemon

class TestDaemon(unittest.TestCase):
    device_token = '000000000000000000000001'

    def setUp(self):
        self.daemon = Daemon()

    def method_exists(self, method):
        self.assertTrue(inspect.ismethod(method))

    def testDefauls(self):
        self.assertIsNotNone(self.daemon)
        self.assertIsNone(self.daemon.token)

        self.method_exists(self.daemon.set_device_token)
        self.method_exists(self.daemon.read_persistent)

    def testSetDeviceToken(self):
        self.assertIsNone(self.daemon.token)
        self.daemon.set_device_token(self.device_token)
        self.assertEqual(self.daemon.token, self.device_token)

    @staticmethod
    def _mockVariableHandler(var):
        var['value'] = var['value'] + 1


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


def main():
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)

if __name__ == '__main__':
    main()
