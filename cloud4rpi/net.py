# -*- coding: utf-8 -*-

import socket
import logging
import cloud4rpi.config

log = logging.getLogger(cloud4rpi.config.loggerName)


class Hostname(object):
    def __init__(self):
        self.__host = None

    def read(self):
        if self.__host is None:
            self.__read()
        return self.__host

    def __read(self):
        try:
            self.__host = socket.gethostname()
        except Exception as e:
            log.error('Gathering host information has failed: %s', e)


def connect_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 80))
    return sock


class IPAddress(object):
    def __init__(self):
        self.__addr = None

    def read(self):
        if self.__addr is None:
            self.__read()
        return self.__addr

    def __read(self):
        sock = None
        try:
            sock = connect_socket()
            (self.__addr, _) = sock.getsockname()
        except Exception as e:
            msg = 'Gathering ip address information has failed: {0}'.format(e)
            log.error(msg)
        finally:
            if sock is not None:
                sock.close()
