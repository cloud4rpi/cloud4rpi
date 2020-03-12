from os import path
from setuptools import setup

description = ''

try:
    import pypandoc  # pylint: disable=F0401

    description = pypandoc.convert('README.md', 'rst')
except Exception:
    pass

v = path.join('cloud4rpi', 'version.py')
with open(v) as f:
    version_code = compile(f.read(), v, 'exec')
    exec(version_code)

setup(name='cloud4rpi',
      version=__version__,
      description='Cloud4RPi client library',
      long_description=description,
      url='https://github.com/cloud4rpi/cloud4rpi',
      author='Cloud4RPi team',
      author_email='team@cloud4rpi.io',
      license='MIT',
      packages=['cloud4rpi'],
      install_requires=[
          'paho-mqtt'
      ])
