#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from subprocess import CalledProcessError
from c4r.logger import get_logger
from c4r.mqtt_listener import stop_listen


log = get_logger()


def modprobe(module):
    cmd = 'modprobe {0}'.format(module)
    ret = os.system(cmd)
    if ret != 0:
        raise CalledProcessError(ret, cmd)


def finalize():
    stop_listen()
    print 'STOPPED'
