#!/usr/bin/env python
import os
import re

FILE_NAME = 'cloud4rpid.sh'
PATTERN = '%%CLOUD4RPI_DIR%%'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def patch(fileName, fromString, toString):
    with open(fileName) as f:
        out_fname = fileName + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(fromString, toString, line))
        out.close()
        os.rename(out_fname, fileName)

if __name__ == "__main__":
    print CURRENT_DIR
    patch(FILE_NAME, PATTERN, CURRENT_DIR)
