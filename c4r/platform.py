#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

class platform(object):
    @staticmethod
    def get():
        if subprocess.check_output("uname -a", shell=True).find('Linux chip') == 0:
            return "CHIP"
        else:
            return "RPI"
        return "Unknown"

# TODO: Get once and cache result
