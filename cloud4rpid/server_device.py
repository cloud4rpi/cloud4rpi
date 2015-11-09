class ServerDevice(object):
    def __init__(self, device_json):
        self.json = device_json
        self.addresses = None
        self.extension_index = None
        self.__build_extension_index()
        self.__extract_addresses()

    def extension_addrs(self):
        return self.addresses

    def add_sensors(self, sensors):
        self.json['sensors'] += [{'name': x, 'address': x} for x in sensors]
        self.__extract_addresses()

    def add_actuators(self, actuators):
        self.json['actuators'] += actuators
        self.__extract_addresses()

    def add_variables(self, variables):
        self.json['variables'] += variables
        self.__extract_addresses()

    def get_actuators(self):
        return [x['_id'] for x in self.json['actuators']]

    def whats_new(self, extensions):
        existing = self.extension_addrs()
        return set(extensions) - set(existing)

    def dump(self):
        return self.json

    def map_extensions(self, readings):
        index = self.extension_index
        return {index[address]: reading for address, reading in readings if address in index}

    def set_type(self, new_type):
        self.json['type'] = new_type

    def __extract_addresses(self):
        self.addresses = self.extension_index.keys()

    def __build_extension_index(self):
        extensions = self.json['sensors'] + self.json['actuators'] + self.json['variables']
        if len(extensions) == 0:
            self.extension_index = {}
        else:
            self.extension_index = \
                {extension.get('address', extension.get('name')): extension.get('_id', extension.get('name'))
                 for extension in extensions}
