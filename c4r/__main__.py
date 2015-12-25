#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from subprocess import CalledProcessError
import requests
from c4r.logger import get_logger


log = get_logger()


def modprobe(module):
    cmd = 'modprobe {0}'.format(module)
    ret = os.system(cmd)
    if ret != 0:
        raise CalledProcessError(ret, cmd)


def safe_run_daemon(lib):
    max_try_count = 5
    wait_secs = 10
    n = 0
    while n < max_try_count:
        try:
            lib.set_device_token(DeviceToken)
            break
        except requests.ConnectionError as ex:
            log.exception('Daemon running ERROR: {0}'.format(ex.message))
            log.exception('Waiting for {0} sec...'.format(wait_secs))
            time.sleep(wait_secs)
            n += 1
            wait_secs *= 2

