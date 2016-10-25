#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import CalledProcessError
from mqtt_client import InvalidTokenError

messages = {
    KeyboardInterrupt: 'Interrupted',
    CalledProcessError: 'Try run with sudo',
    InvalidTokenError: 'Device token {0} is invalid. Please verify it.',
}


def get_error_message(e):
    return messages.get(type(e), 'Unexpected error: {0}').format(e.message)
