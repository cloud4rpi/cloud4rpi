import glob


def extract_temperature(s):
    index = s.find('t=')
    if index > 0:
        index += 2
        res = s[index:]
        return float(res) / 1000
    return 0


class Sensor():
    NAME = ''
    W1PATH = ''

    def __init__(self, name, w1path):
        self.NAME = name
        self.W1PATH = w1path

    def get_id(self):
        return self.NAME

    def get_data(self):
        # find the path of a sensor directory
        devicelist = glob.glob(self.W1PATH)

        # append the device file name to get the absolute path of the sensor
        devicefile = devicelist[0] + '/w1_slave'

        # open the file representing the sensor.
        fileobj = open(devicefile, 'r')
        lines = fileobj.readlines()
        fileobj.close()

        # print the lines read from the sensor apart from the extra \n chars
        line = lines[1][:-1]
        data = extract_temperature(line)
        return data
