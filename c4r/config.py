#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Server parameters
baseApiUrl = 'https://cloud4rpi.io/api'


# MQTT broker parameters
mqqtBrokerHost = 'sky3d-macbook'
mqttBrokerPort = 1883
mqqtBrokerUsername = 'c4r-user'
mqttBrokerPassword = 'c4r-password'

mqttTopicRoot = 'iot-hub'
mqttMessageTopicPrefix = mqttTopicRoot + '/messages'
mqttCommandsTopicPrefix = mqttTopicRoot + '/commands'


# logging
LOG_FILE_NAME = 'cloud4rpi.log'
