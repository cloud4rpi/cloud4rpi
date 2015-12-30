#!/usr/bin/env python
import os
import re

TEMPLATE_FILE_NAME = 'cloud4rpi.tmpl'
FILE_NAME = 'tmp/cloud4rpi'

PATTERN = '%%CLOUD4RPI_DIR%%'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def generateFromTemplate():
    with open(TEMPLATE_FILE_NAME) as f:
        out = open(FILE_NAME, "w")
        for line in f:
            out.write(re.sub(PATTERN, CURRENT_DIR, line))
        out.close()

if __name__ == "__main__":
    print 'Current directory: ', CURRENT_DIR
    generateFromTemplate()
