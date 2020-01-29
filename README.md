## **Cloud4RPi** is a cloud control panel for your [IoT](https://en.wikipedia.org/wiki/Internet_of_things) device.

[![Build Status](https://travis-ci.org/cloud4rpi/cloud4rpi.svg?branch=master)](https://travis-ci.org/cloud4rpi/cloud4rpi)

This package provides a client library that simplifies the connection to the [Cloud4RPi](https://cloud4rpi.io/) service.

## Cloud4RPi Features

-   Use widgets to display device data and send commands in real time.
-   Control your IoT devices remotely.
-   Connect any device to **Cloud4RPi**.
-   Use [MQTT](https://pypi.python.org/pypi/paho-mqtt) or HTTP to send data and receive control commands.

## Start Using

1. Install this package:

    Install the library using your preferred Python version.
    The following command installs and integrates Cloud4RPi with your OS's default Python interpreter (usually Python 3):

    ```bash
     sudo pip3 install cloud4rpi
    ```

    If you are using Python 2, use the following command:

    ```bash
    sudo python2 -m pip install cloud4rpi
    ```

2. Get examples for your platform:
    - [Raspberry Pi](https://github.com/cloud4rpi/cloud4rpi-raspberrypi-python): `wget https://github.com/cloud4rpi/cloud4rpi-raspberrypi-python/archive/master.zip && unzip master.zip && rm master.zip && cd cloud4rpi-raspberrypi-python-master`
    - [C.H.I.P.](https://github.com/cloud4rpi/cloud4rpi-chip-python): `wget https://github.com/cloud4rpi/cloud4rpi-chip-python/archive/master.zip && unzip master.zip && rm master.zip && cd cloud4rpi-chip-python-master`
    - [Omega2](https://github.com/cloud4rpi/cloud4rpi-omega2-python): `r="https://raw.githubusercontent.com/cloud4rpi/cloud4rpi-omega2-python/master" && wget $r"/omega2.py" $r"/led.py" $r"/rgb_led.py"`
    - [ESP8266 on MicroPython](https://github.com/cloud4rpi/cloud4rpi-esp8266-micropython)
    - [ESP8266/ESP32 on Arduino framework](https://github.com/cloud4rpi/cloud4rpi-esp-arduino)
3. Create a free account on [Cloud4RPi](https://cloud4rpi.io).
4. Create a device on the [Devices](https://cloud4rpi.io/devices) page.
5. Copy the **Device Token** from the device page.
6. Replace the `__YOUR_DEVICE_TOKEN__` string in one of the examples with your real device token.
7. Run the example with `python` (if you use ESP8266, upload the required files to the board and reset it).
8. Create your own scripts based on the examples.

For detailed instructions, refer to the [documentation](http://docs.cloud4rpi.io/) and corresponding repositories.

## See Also

-   [GitHub Repository](https://github.com/cloud4rpi/cloud4rpi/)
-   [Cloud4RPi Gists](https://gist.github.com/c4r-gists)
-   [PyPI Package](https://pypi.python.org/pypi/cloud4rpi)
-   [Documentation Repository](https://github.com/cloud4rpi/docs)
-   [Usage Examples for Raspberry Pi](https://github.com/cloud4rpi/cloud4rpi-raspberrypi-python)
-   [Usage Examples for Next Thing Co. C.H.I.P.](https://github.com/cloud4rpi/cloud4rpi-chip-python)
-   [Usage Examples for Onion Omega2](https://github.com/cloud4rpi/cloud4rpi-omega2-python)
-   [Usage Examples for ESP8266 on MicroPython](https://github.com/cloud4rpi/cloud4rpi-esp8266-micropython)
-   [Usage Examples for ESP8266/ESP32 on Arduino framework](https://github.com/cloud4rpi/cloud4rpi-esp-arduino)
