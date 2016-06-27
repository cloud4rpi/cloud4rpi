import socket
import os
from c4r.logger import get_logger

log = get_logger()

ipaddr = None
host = None

try:
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ipaddr = s.getsockname()[0]
    host = socket.gethostname()

except Exception as e:
    log.error('Gathering network information failed: {0}'.format(e))


def get_network_info():
    return {'ipaddr': ipaddr, 'host': host}
