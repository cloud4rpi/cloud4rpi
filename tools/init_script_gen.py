#!/usr/bin/env python
import os
import re


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PATTERN = '%%CLOUD4RPI_DIR%%'
FILE_NAME = 'tmp/cloud4rpi'


def get_template_path():
    return os.path.join(CURR_DIR, 'cloud4rpi.tmpl')


def get_target_path():
    return os.path.abspath(os.path.join(CURR_DIR, '../'))


TARGET_PATH = get_target_path()


def generate_from_template():
    template_path = get_template_path()
    with open(template_path) as f:
        out = open(FILE_NAME, "w")
        for line in f:
            out.write(re.sub(PATTERN, TARGET_PATH, line))
        out.close()

if __name__ == "__main__":
    print 'Target directory: ', TARGET_PATH
    generate_from_template()
