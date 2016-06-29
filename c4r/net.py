import socket
import os
from c4r.logger import get_logger

log = get_logger()


def connect_socket():
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    return s


class NetworkInfo(object):
    def __init__(self):
        self.ipaddr = None
        self.host = None

        self.get_network_info()

    def get_ipaddress(self):
        return self.ipaddr

    def get_host(self):
        return self.host

    def get_network_info(self):
        try:
            self.host = socket.gethostname()
            s = connect_socket()
            self.ipaddr = s.getsockname()[0]
        except Exception as e:
            log.error('Gathering network information failed: {0}'.format(e))
