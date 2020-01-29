# -*- coding: utf-8 -*-

from cloud4rpi import utils


class Device(object):
    def __init__(self, api):
        def on_command(cmd):
            self.__on_command(cmd)

        self.__api = api
        self.__api.on_command = on_command
        self.__variables = {}
        self.__diag = {}

    @staticmethod
    def __resolve_binding(binding, current=None, default=None):
        if hasattr(binding, 'read'):
            return binding.read()
        elif callable(binding):
            return utils.resolve_callable(binding, current)
        else:
            return default

    def __validate_payload(self, payload):
        result = {}
        for name, value in payload.items():
            variable = self.__variables.get(name, None)
            if not variable:
                continue
            t = variable.get('type', None)
            result[name] = utils.validate_variable_value(name, t, value)

        return result

    def __on_command(self, cmd):
        update = self.__apply_commands(cmd)
        if bool(update):
            self.__api.publish_data(update, data_type='cr')

    def __apply_commands(self, cmd):
        update = {}
        for varName, value in cmd.items():
            variable = self.__variables.get(varName, None)
            if not variable:
                continue
            # consider to use resolve binding here
            new_value = value
            handler = variable.get('bind', None)
            if callable(handler):
                new_value = handler(new_value)

            t = variable.get('type', None)
            new_value = utils.validate_variable_value(varName, t, new_value)
            variable['value'] = new_value

            update[varName] = new_value

        return update

    def declare(self, variables):
        for name, value in variables.items():
            utils.guard_against_invalid_variable_type(name,
                                                      value.get('type', None))
        self.__variables = variables

    def declare_diag(self, diag):
        self.__diag = diag

    def read_config(self):
        return [{'name': name, 'type': value['type']}
                for name, value in self.__variables.items()]

    def read_data(self):
        for name, varConfig in self.__variables.items():
            bind = varConfig.get('bind', None)
            if bind:
                curr = varConfig.get('value')
                result = self.__resolve_binding(bind, curr, curr)
                t = varConfig.get('type')
                new_val = utils.validate_variable_value(name, t, result)
                varConfig['value'] = new_val

        readings = {varName: varConfig.get('value')
                    for varName, varConfig in self.__variables.items()}

        return readings

    def read_diag(self):
        readings = {}
        for name, value in self.__diag.items():
            readings[name] = self.__resolve_binding(value, None, value)
        return readings

    def publish_config(self, cfg=None):
        if cfg is None:
            cfg = self.read_config()
        else:
            cfg = utils.validate_config(cfg)

        return self.__api.publish_config(cfg)

    def publish_data(self, data=None):
        if data is None:
            data = self.read_data()
        else:
            data = self.__validate_payload(data)

        return self.__api.publish_data(data)

    def publish_diag(self, diag=None):
        if diag is None:
            diag = self.read_diag()
        return self.__api.publish_diag(diag)
