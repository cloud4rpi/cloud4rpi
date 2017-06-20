# -*- coding: utf-8 -*-

import re
import inspect
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


def args_count(binding):
    # pylint: disable=E1101, W1505
    if inspect.getargspec is not None:
        args = inspect.getargspec(binding).args
    else:
        args = inspect.getfullargspec(binding).args

    return args.__len__()


def resolve_method_binding(binding, current=None):
    if args_count(binding) > 1:
        return binding(current)
    else:
        return binding()


def resolve_func_binding(binding, current=None):
    if args_count(binding) > 0:
        return binding(current)
    else:
        return binding()
