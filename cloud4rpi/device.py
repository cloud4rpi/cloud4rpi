# -*- coding: utf-8 -*-

import inspect


class Device(object):
    def __init__(self, api):
        def on_command(cmd):
            self.__on_command(cmd)

        self.__api = api
        self.__api.on_command = on_command
        self.__variables = {}
        self.__diag = {}

    @staticmethod
    def __resolve_binding(binding, current=None):
        if hasattr(binding, 'read'):
            return binding.read()
        elif callable(binding):
            if inspect.getargspec(binding).args.__len__() == 0:
                return binding()
            else:
                return binding(current)
        else:
            return binding

    @staticmethod
    def __validate_bool_var(variable, value):
        return bool(value) \
            if variable.get('type', None) == 'bool' \
            else value

    def __on_command(self, cmd):
        actual_var_values = {}
        for varName, value in cmd.items():
            variable = self.__variables.get(varName, {})
            handler = variable.get('bind', None)
            if not callable(handler):
                continue
            actual = handler(value)
            if actual is None:
                continue

            actual = self.__validate_bool_var(variable, value)
            actual_var_values[varName] = actual
            variable['value'] = actual
        self.__api.publish_data(actual_var_values)

    def declare(self, variables):
        self.__variables = variables
        self.send_config()

    def declare_diag(self, diag):
        self.__diag = diag

    def send_data(self):
        for _, varConfig in self.__variables.items():
            bind = varConfig.get('bind', None)
            if bind:
                new_val = self.__resolve_binding(bind, varConfig.get('value'))
                new_val = self.__validate_bool_var(varConfig, new_val)
                varConfig['value'] = new_val

        readings = {varName: varConfig.get('value')
                    for varName, varConfig in self.__variables.items()}
        if len(readings) == 0:
            return

        self.__api.publish_data(readings)

    def send_diag(self):
        readings = {}
        for name, value in self.__diag.items():
            readings[name] = self.__resolve_binding(value)
        self.__api.publish_diag(readings)

    def send_config(self):
        declarations = [{'name': name, 'type': value['type']}
                        for name, value in self.__variables.items()]
        self.__api.publish_config(declarations)
