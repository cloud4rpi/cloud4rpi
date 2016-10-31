from setuptools import setup

import pypandoc


def readme():
    return pypandoc.convert('README.md', 'rst')


setup(name='cloud4rpi',
      version='0.0.2',
      description='Easily connect your Raspberry Pi to the Internet',
      long_description=readme(),
      url='https://github.com/cloud4rpi/cloud4rpi',
      author='cloud4rpi team',
      author_email='cloud4rpi@gmail.com',
      license='MIT',
      packages=['cloud4rpi'],
      install_requires=[
          'paho-mqtt',
      ])
