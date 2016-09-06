#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from subprocess import CalledProcessError
from c4r.timer import RecurringTimer
from c4r.api import send_system_info

from c4r.logger import get_logger
from c4r.logger import set_logger_level
from c4r.logger import set_logging_to_file

from c4r.mqtt_listener import stop_listen


log = get_logger()
timer = None


def modprobe(module):
    cmd = 'modprobe {0}'.format(module)
    ret = os.system(cmd)
    if ret != 0:
        raise CalledProcessError(ret, cmd)


def start_polling(interval=60):
    log.debug('start pooling')
    global timer
    timer = RecurringTimer(interval, send_system_info)
    timer.start()


def cleanup():
    timer.stop()  # stop sending system diagnostic data
    stop_listen()
    log.info('STOPPED')
