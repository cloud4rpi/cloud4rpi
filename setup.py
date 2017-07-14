from setuptools import setup

description = ''

try:
    import pypandoc  # pylint: disable=F0401

    description = pypandoc.convert('README.md', 'rst')
except Exception:
    pass

setup(name='cloud4rpi',
      version='0.0.51',
      description='cloud4rpi client library',
      long_description=description,
      url='https://github.com/cloud4rpi/cloud4rpi',
      author='cloud4rpi team',
      author_email='cloud4rpi@gmail.com',
      license='MIT',
      packages=['cloud4rpi'],
      install_requires=[
          'paho-mqtt',
          'requests',
          'arrow',
      ])
