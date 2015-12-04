#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from subprocess import CalledProcessError
import requests
from requests import RequestException

import c4r.errors as errors
from c4r import lib
from settings import DeviceToken
from c4r.logger import get_logger, config_logging_to_file
from settings import LOG_FILE_PATH


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
            # lib.run()
            break
        except requests.ConnectionError as ex:
            log.exception('Daemon running ERROR: {0}'.format(ex.message))
            log.exception('Waiting for {0} sec...'.format(wait_secs))
            time.sleep(wait_secs)
            n += 1
            wait_secs *= 2

# TODO remove it
def main():
    daemon = None
    try:
        modprobe('w1-gpio')
        modprobe('w1-therm')

        config_logging_to_file(log, LOG_FILE_PATH)

        log.info('Starting...')

        safe_run_daemon(lib)

    except RequestException as e:
        log.exception('Connection failed. Please try again later. Error: {0}'.format(e.message))
        exit(1)
    except CalledProcessError:
        log.exception('Try "sudo python cloud4rpi.py"')
        exit(1)
    except errors.InvalidTokenError:
        log.exception('Device Access Token {0} is incorrect. Please verify it.'.format(DeviceToken))
        exit(1)
    except errors.AuthenticationError:
        log.exception('Authentication failed. Check your device token.')
        exit(1)
    except errors.NoSensorsError:
        log.exception('No sensors found... Exiting')
        exit(1)
    except Exception as e:
        log.exception('Unexpected error: {0}'.format(e.message))
        exit(1)
    except KeyboardInterrupt:
        log.info('Interrupted')
        if daemon:
            daemon.shutdown()
        exit(1)


if __name__ == "__main__":
    main()
