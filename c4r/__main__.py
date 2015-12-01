#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import logging.handlers
from subprocess import CalledProcessError
import cloud4rpi.errors as errors
from settings import LOG_FILE_PATH

import requests
from requests import RequestException

def create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    config_logging_to_console(logger)
    return logger


def config_logging_to_console(logger):
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console)


def config_logging_to_file(logger):
    log_file = logging.handlers.RotatingFileHandler(LOG_FILE_PATH, maxBytes=1024 * 1024, backupCount=10)
    log_file.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(log_file)

log = create_logger()

def modprobe(module):
    cmd = 'modprobe {0}'.format(module)
    ret = os.system(cmd)
    if ret != 0:
        raise CalledProcessError(ret, cmd)


def safe_run_daemon(daemon):
    max_try_count = 5
    wait_secs = 10
    n = 0
    while n < max_try_count:
        try:
            daemon.set_device_token(DeviceToken)
            daemon.run()
            break
        except requests.ConnectionError as ex:
            log.exception('Daemon running ERROR: {0}'.format(ex.message))
            log.exception('Waiting for {0} sec...'.format(wait_secs))
            time.sleep(wait_secs)
            n += 1
            wait_secs *= 2


from c4r.daemon import Daemon
from settings import DeviceToken

def main():
    daemon = None
    try:
        modprobe('w1-gpio')
        modprobe('w1-therm')

        config_logging_to_file(log)

        log.info('Starting...')

        daemon = Daemon()
        safe_run_daemon(daemon)

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
