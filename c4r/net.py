import socket
import os
from c4r.logger import get_logger
from c4r.helpers import get_by_key

log = get_logger()

NETWORK_HOST_PARAM = 'host'
NETWORK_ADDR_PARAM = 'addr'


def connect_socket():
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    return s


def get_network_info():
    result = {}
    try:
        result[NETWORK_HOST_PARAM] = socket.gethostname()
        s = connect_socket()
        result[NETWORK_ADDR_PARAM] = s.getsockname()[0]
    except Exception as e:
        log.error('Gathering network information failed: {0}'.format(e))

    return result


class NetworkInfo(object):
    def __init__(self):
        self.info = {}

    def read(self):
        self.info = get_network_info()

    @property
    def addr(self):
        return get_by_key(self.info, NETWORK_ADDR_PARAM)

    @property
    def host(self):
        return get_by_key(self.info, NETWORK_HOST_PARAM)
