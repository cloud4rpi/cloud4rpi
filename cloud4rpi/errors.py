# -*- coding: utf-8 -*-

import subprocess

TYPE_WARN_MSG = 'WARNING! A string "%s" passed to a numeric variable. ' \
                'Change the variable type or the passed value.' \



class InvalidTokenError(Exception):
    pass


class InvalidConfigError(TypeError):
    pass


class UnexpectedVariableTypeError(TypeError):
    pass


class UnexpectedVariableValueTypeError(TypeError):
    pass


class MqttConnectionError(Exception):
    def __init__(self, code):
        super(MqttConnectionError, self).__init__()
        self.code = code


class NotSupportedError(Exception):
    pass


__messages = {
    KeyboardInterrupt: 'Interrupted',
    subprocess.CalledProcessError: 'Try run with sudo',
    InvalidTokenError:
        'Device token {0} is invalid. Please verify it.',
    InvalidConfigError:
        'Configuration is invalid. It must be an array.',
    UnexpectedVariableTypeError:
        ('Unexpected type for the "{0}" variable. '
         'It must be "bool", "numeric", "string" or "location".'),
    UnexpectedVariableValueTypeError:
        'Unexpected value type for variable: {0}'
}


def get_error_message(e):
    msg = getattr(e, 'message', repr(e))
    return __messages.get(type(e), 'Unexpected error: {0}').format(msg)
