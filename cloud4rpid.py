#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import os
import re
import traceback
import ConfigParser
import requests
import settings
import amqp

import sensorDS18B20 as sensor

configFileName = 'config.cfg'
config = ConfigParser.SafeConfigParser()
sensors = []


class RpiDaemon():
    def __init__(self):
        pass

    def run(self):
        print 'Rpi data output daemon running... '

        # probe w1 modules
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        self.load_config()
        self.detect_sensors()
        self.save_config()
        self.poll_sensors()
        print 'Done'

    def load_config(self):
        config.read(configFileName)
        if not config.has_section('Sensors'):
            config.add_section('Sensors')
        if not config.has_section('Config'):
            config.add_section('Config')
        if not config.has_option('Config', 'DeviceId'):
            self.register_device()

    @staticmethod
    def save_config():
        with open(configFileName, 'wb') as configfile:
            config.write(configfile)

    def post_sensor_data(self, sensors_data):
        deviceId = config.get('Config', 'DeviceId')
        url = 'devices/%s/streams' % deviceId

        data = sensors_data
        data["device"] = deviceId
        amqp.publish(data)
        return 0 #TODO

    def create_sensors(self, new_sensors):
        url = 'devices/%s/sensors' % config.get('Config', 'DeviceId')
        r = self.post_data(url, new_sensors)
        if r.status_code != 201:
            raise Exception("Can\'t register sensor. Status: %s" % r.status_code)

        return r.json()

    def create_device(self, device_name):
        url = 'devices'
        data = {'name': device_name}
        r = self.post_data(url, data)
        if r.status_code != 201:
            raise Exception("Can\'t register device. Status: %s" % r.status_code)

        return r.json()['_id']


    @staticmethod
    def post_data(url, data):
        try:
            headers = {"Content-type": "application/json", "api_key": settings.AccessToken}
            r = requests.post(settings.baseApiUrl + url, headers=headers, data=json.dumps(data))

            return r

        except Exception, err:
            print traceback.format_exc()

    @staticmethod
    def get_sensor_data(sensors):
        result = {}
        result["ts"] = time.time()

        payload = {}
        for sensor in sensors:
            payload[sensor.get_id()] = sensor.get_data()

        result["payload"] = payload
        return result

    def detect_sensors(self):
        r = re.compile('(10|22|28)-.*')
        for dirname, dirnames, filenames in os.walk('/sys/bus/w1/devices/'):
            new_sensors = []
            for deviceFileName in dirnames:
                if not r.match(deviceFileName):
                    print 'Unknown device type. Skipping. ' + deviceFileName
                    continue
                if not config.has_option('Sensors', deviceFileName):
                    new_sensors.append({'name': deviceFileName})
                else:
                    sensors.append(
                        sensor.Sensor(config.get('Sensors', deviceFileName), os.path.join(dirname, deviceFileName)))
            if len(new_sensors) > 0:
                self.register_sensor(new_sensors)
                # TODO make it better
                sensors[:] = []
                self.detect_sensors()

    def poll_sensors(self):
        n = 1
        while 1:
            try:
                data = self.get_sensor_data(sensors)
                print data
                r = self.post_sensor_data(data)
                # TODO catch exceptions
                #print r.status_code
                print r

                # if r.status_code == 401:
                #     print "Error! 401 - Unauthorized request."
                #     print "Process interrupted. Please verify your AccessToken is valid"
                #     sys.exit(1)

                n += 1
            except Exception, err:
                print traceback.format_exc()
            time.sleep(settings.scanInterval)

    def register_sensor(self, new_sensors):
        print '%s new devices found' % len(new_sensors)
        created_sensors = self.create_sensors(new_sensors)
        for sensor in created_sensors:
            print '%s: %s' % (sensor['name'], sensor['_id'])
            config.set('Sensors', sensor['name'], sensor['_id'])

    def register_device(self):
        print 'No DeviceId found. Registering device'
        created_device_id = self.create_device('New device')
        print 'createdDeviceId: ' + created_device_id
        config.set('Config', 'DeviceId', created_device_id)
        return created_device_id


if __name__ == "__main__":
    daemon = RpiDaemon()
    daemon.run()
