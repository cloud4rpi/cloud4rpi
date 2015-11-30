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


    def testSetDeviceToken(self):
        self.assertIsNone(self.daemon.token)
        self.daemon.set_device_token(self.device_token)
        self.assertEqual(self.daemon.token, self.device_token)


def main():
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)

if __name__ == '__main__':
    main()
