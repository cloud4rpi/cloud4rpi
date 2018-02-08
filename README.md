**Cloud4RPi** is a cloud control panel for your [IoT](https://en.wikipedia.org/wiki/Internet_of_things) device.
-----
[![Build Status](https://travis-ci.org/cloud4rpi/cloud4rpi.svg?branch=master)](https://travis-ci.org/cloud4rpi/cloud4rpi)

This package provides a client library that simplifies the connection to the [Cloud4RPi](https://cloud4rpi.io/) service.


## Cloud4RPi Features

- Use widgets to display device data and send commands in real time.
- Control your IoT devices remotely.
- Connect any device to **Cloud4RPi**.
- Use [MQTT](https://pypi.python.org/pypi/paho-mqtt) or HTTP to send data and receive control commands.

## Start Using

1. Install this package:
    ```bash
    sudo pip install cloud4rpi
    ```
1. Get examples for your platform:
    - [Raspberry Pi](https://github.com/cloud4rpi/cloud4rpi-raspberrypi-python): `wget https://github.com/cloud4rpi/cloud4rpi-raspberrypi-python/archive/master.zip && unzip master.zip && rm master.zip && cd cloud4rpi-raspberrypi-python-master`
    - [C.H.I.P.](https://github.com/cloud4rpi/cloud4rpi-chip-python): `wget https://github.com/cloud4rpi/cloud4rpi-chip-python/archive/master.zip && unzip master.zip && rm master.zip && cd cloud4rpi-chip-python-master`
    - [Omega2](https://github.com/cloud4rpi/cloud4rpi-omega2-python): `r="https://raw.githubusercontent.com/cloud4rpi/cloud4rpi-omega2-python/master" && wget $r"/omega2.py" $r"/led.py" $r"/rgb_led.py"`
    - [ESP8266 on MicroPython](https://github.com/cloud4rpi/cloud4rpi-esp8266-micropython)
    - [ESP8266 on Arduino framework](https://github.com/cloud4rpi/cloud4rpi-esp-arduino)
1. Create a free account on [Cloud4RPi](https://cloud4rpi.io).
2. Create a device on the [Devices](https://cloud4rpi.io/devices) page.
3. Copy the **Device Token** from the device page.
4. Replace the `__YOUR_DEVICE_TOKEN__` string in one of the examples with your real device token.
5. Run the example with `python` (if you use ESP8266, upload the required files to the board and reset it).
6. Create your own scripts based on the examples.

For detailed instructions, refer to the [documentation](http://docs.cloud4rpi.io/) and corresponding repositories.

## See Also

* [GitHub Repository](https://github.com/cloud4rpi/cloud4rpi/)
* [Cloud4RPi Gists](https://gist.github.com/c4r-gists)
* [PyPI Package](https://pypi.python.org/pypi/cloud4rpi)
* [Documentation Repository](https://github.com/cloud4rpi/docs)
* [Usage Examples for Raspberry Pi](https://github.com/cloud4rpi/cloud4rpi-raspberrypi-python)
* [Usage Examples for Next Thing Co. C.H.I.P.](https://github.com/cloud4rpi/cloud4rpi-chip-python)
* [Usage Examples for Onion Omega2](https://github.com/cloud4rpi/cloud4rpi-omega2-python)
* [Usage Examples for ESP8266 on MicroPython](https://github.com/cloud4rpi/cloud4rpi-esp8266-micropython)
* [Usage Examples for ESP8266 on Arduino framework](https://github.com/cloud4rpi/cloud4rpi-esp-arduino)
