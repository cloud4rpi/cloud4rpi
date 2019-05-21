# -*- coding: utf-8 -*-

import sys
import re
import inspect
import logging
import numbers
from math import isnan, isinf
from datetime import datetime, tzinfo, timedelta
from cloud4rpi import config
from cloud4rpi.errors import InvalidTokenError
from cloud4rpi.errors import InvalidConfigError
from cloud4rpi.errors import UnexpectedVariableTypeError
from cloud4rpi.errors import UnexpectedVariableValueTypeError
from cloud4rpi.errors import TYPE_WARN_MSG

if sys.version_info[0] > 2:
    from cloud4rpi.utils_v3 import is_string
else:
    from cloud4rpi.utils_v2 import is_string

log = logging.getLogger(config.loggerName)

BOOL_TYPE = 'bool'
NUMERIC_TYPE = 'numeric'
STRING_TYPE = 'string'
LOCATION_TYPE = 'location'

SUPPORTED_VARIABLE_TYPES = [BOOL_TYPE, NUMERIC_TYPE, STRING_TYPE, LOCATION_TYPE]


class UtcTzInfo(tzinfo):
    # pylint: disable=W0223
    def tzname(self, dt):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


def guard_against_invalid_token(token):
    token_re = re.compile('[1-9a-km-zA-HJ-NP-Z]{23,}')
    if not token_re.match(token):
        raise InvalidTokenError(token)


def to_bool(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, numbers.Number):
        return bool(value)
    else:
        raise Exception()


def to_numeric(value):
    if isinstance(value, bool):
        return float(value)
    elif isinstance(value, numbers.Number):
        return None if isnan(value) or isinf(value) else value
    elif is_string(value):
        log.warning(TYPE_WARN_MSG, value)
        return float(value)
    else:
        raise Exception()


def to_string(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)


def to_location(value):
    if isinstance(value, dict):
        return {x: value[x] for x in ('lat', 'lng')}
    else:
        raise Exception()


def validate_variable_value(name, var_type, value):
    if value is None:
        return value

    convert = {
        BOOL_TYPE: to_bool,
        NUMERIC_TYPE: to_numeric,
        STRING_TYPE: to_string,
        LOCATION_TYPE: to_location
    }
    c = convert.get(var_type, None)
    if c is None:
        return None
    try:
        return c(value)
    except Exception:
        raise UnexpectedVariableValueTypeError('"{0}"={1}'.format(name, value))


def validate_config(cfg):
    if not isinstance(cfg, list):
        raise InvalidConfigError()

    for item in cfg:
        guard_against_invalid_variable_type(
            item.get('name', None),
            item.get('type', None)
        )
    return cfg


def guard_against_invalid_variable_type(name, var_type):
    if var_type not in SUPPORTED_VARIABLE_TYPES:
        raise UnexpectedVariableTypeError(name)


def utcnow():
    return datetime.utcnow().replace(tzinfo=UtcTzInfo()).isoformat()


def args_count(binding):
    # pylint: disable=E1101, W1505
    if inspect.getargspec is not None:
        args = inspect.getargspec(binding).args
    else:
        args = inspect.getfullargspec(binding).args

    return args.__len__()


def has_args(binding):
    if inspect.ismethod(binding):
        return args_count(binding) > 1
    else:
        return args_count(binding) > 0


def resolve_callable(binding, current=None):
    if has_args(binding):
        return binding(current)
    else:
        return binding()
