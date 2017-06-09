# -*- coding: utf-8 -*-

import re
import cloud4rpi.errors
import arrow


def guard_against_invalid_token(token):
    token_re = re.compile('[1-9a-km-zA-HJ-NP-Z]{23,}')
    if not token_re.match(token):
        raise cloud4rpi.errors.InvalidTokenError(token)


def variables_to_config(variables):
    return [{'name': name, 'type': value['type']}
            for name, value in variables.items()]


def utcnow():
    return arrow.utcnow().isoformat()
