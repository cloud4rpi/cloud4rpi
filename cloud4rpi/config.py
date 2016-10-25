#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MQTT broker parameters
mqqtBrokerHost = 'mq.cloud4rpi.io'
mqttBrokerPort = 1883
mqqtBrokerUsername = 'c4r-user'
mqttBrokerPassword = 'c4r-password'

mqttTopicRoot = 'iot-hub'
mqttMessageTopicPrefix = mqttTopicRoot + '/messages'
mqttCommandsTopicPrefix = mqttTopicRoot + '/commands'

loggerName = 'cloud4rpi logger'
