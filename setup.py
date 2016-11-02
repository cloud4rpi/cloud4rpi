from setuptools import setup

description = ''

try:
    import pypandoc

    description = pypandoc.convert('README.md', 'rst')
except Exception:
    pass

setup(name='cloud4rpi',
      version='0.0.5',
      description='cloud4Rpi client library',
      long_description=description,
      url='https://github.com/cloud4rpi/cloud4rpi',
      author='cloud4rpi team',
      author_email='cloud4rpi@gmail.com',
      license='MIT',
      packages=['cloud4rpi'],
      install_requires=[
          'paho-mqtt',
      ])
