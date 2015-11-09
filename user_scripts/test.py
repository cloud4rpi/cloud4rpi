#!/usr/bin/env python2.7


class ExampleScript(object):
    def __init__(self, config, conn):
        pass

    def run(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print 'Cleanup.'
