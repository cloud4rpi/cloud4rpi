from c4r.errors import InvalidTokenError

device_token = None


def set_device_token(token):
    global device_token  # pylint: disable=W0603
    device_token = token


def get_device_token():
    global device_token  # pylint: disable=W0603
    if device_token is None:
        raise InvalidTokenError
    return device_token


def reset_token():
    global device_token  # pylint: disable=W0603
    device_token = None
