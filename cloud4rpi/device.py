# -*- coding: utf-8 -*-

import inspect
from cloud4rpi import utils


class Device(object):
    def __init__(self):
        self.__variables = {}
        self.__diag = {}

    @staticmethod
    def __resolve_binding(binding, current=None):
        if hasattr(binding, 'read'):
            return binding.read()
        elif callable(binding):
            if inspect.ismethod(binding):
                return utils.resolve_method_binding(binding, current)
            else:
                return utils.resolve_func_binding(binding, current)
        else:
            return binding

    @staticmethod
    def __validate_bool_var(variable, value):
        return bool(value) \
            if variable.get('type', None) == 'bool' \
            else value

    def declare(self, variables):
        self.__variables = variables

    def declare_diag(self, diag):
        self.__diag = diag

    def read_config(self):
        return [{'name': name, 'type': value['type']}
                for name, value in self.__variables.items()]

    def read_data(self):
        for _, varConfig in self.__variables.items():
            bind = varConfig.get('bind', None)
            if bind:
                new_val = self.__resolve_binding(bind, varConfig.get('value'))
                new_val = self.__validate_bool_var(varConfig, new_val)
                varConfig['value'] = new_val

        readings = {varName: varConfig.get('value')
                    for varName, varConfig in self.__variables.items()}

        return readings

    def read_diag(self):
        readings = {}
        for name, value in self.__diag.items():
            readings[name] = self.__resolve_binding(value)
        return readings

    def handle_mqtt_commands(self, api):
        def wrapped(cmd):
            self.apply_commands(cmd)
            data = self.read_data()
            if data is not None:
                api.publish_data(data)

        return wrapped

    def apply_commands(self, cmd):
        for varName, value in cmd.items():
            variable = self.__variables.get(varName, {})

            handler = variable.get('bind', None)
            if not callable(handler):
                continue
            actual = handler(value)
            if actual is None:
                continue
            variable['value'] = self.__validate_bool_var(variable, value)
