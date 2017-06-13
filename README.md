**Cloud4RPI** is a cloud control panel for your [IoT](https://en.wikipedia.org/wiki/Internet_of_things) device.

This package provides a client library that simplifies the connection to the **Cloud4RPI** service.


## Cloud4RPI Features

- You can use widgets to display device data and send commands in real time.
- You can control your IoT devices remotely.
- You can connect any device to **Cloud4RPI**.
- You can use [MQTT](https://pypi.python.org/pypi/paho-mqtt) or HTTP to send data and receive control commands.

## Start Using

1. Install this package:
    ```bash
    sudo pip install cloud4rpi
    ```
1. Get examples:
    ```bash
    wget https://github.com/cloud4rpi/cloud4rpi-examples/archive/master.zip && unzip master.zip && rm master.zip
    ```
1. Create a free account on [Cloud4RPI](https://cloud4rpi.io).
2. Create a device on the [Devices](https://cloud4rpi.io/devices) page.
3. Copy the **Device Token** from the device page.
4. Replace the `__YOUR_DEVICE_TOKEN__` string in one of the examples with your real device token.
5. Run the example with `python`.
6. Read the sample code and write your own code!

For detailed instructions, refer to the [documentation](https://cloud4rpi.github.io/docs/).

## Source Code

The source code of this package is available on [GitHub](https://github.com/cloud4rpi/cloud4rpi).

## See Also

* [PyPI Package](https://pypi.python.org/pypi/cloud4rpi)
