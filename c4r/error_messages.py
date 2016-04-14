#!/usr/bin/env python
# -*- coding: utf-8 -*-

from requests import RequestException
from subprocess import CalledProcessError
from c4r import errors as c4r_errors

messages = {
    KeyboardInterrupt: 'Interrupted',
    RequestException: 'Connection failed. Please try again later. Error: {0}',
    CalledProcessError: 'Try "sudo python cloud4rpi.py"',
    c4r_errors.InvalidTokenError: 'Device Access Token {0} is incorrect. Please verify it.',
    c4r_errors.AuthenticationError: 'Authentication failed. Check your device token.',
    KeyError: 'Key "{0}" not found in server response.'
}


def get_error_message(e):
    return messages.get(type(e), 'Unexpected error: {0} - {1}').format(e.message, type(e))
