import yaml
import os

from importlib import import_module

from spectralEIT.bin.default_config import LIST_TYPES, NUMBER_TYPES

class YamlImport():

    def set_attributes(self, _data, _object=None):
        
        # print("################################################")
        # print("inside YamlImport set_data")
        # print(_data)
        # print("################################################")
        
        if _object == None:
            _object = self

        def load_func(string):
            module_, func = string.rsplit(".", maxsplit=1)
            m = import_module('spectralEIT.bin.' + module_)
            return getattr(m, func)

        def check_str(string):
            if "custom_function" in string:
                return load_func(string)
            try:
                return eval(string)
            except:
                return string

        def get_data(data):
            if type(data) in NUMBER_TYPES:
                return data
            if type(data) == str:
                return check_str(data)
            if type(data) in LIST_TYPES:
                tmp_list = []
                for value in data:
                    tmp_list.append( get_data(value) )
                return tmp_list
            if type(data) == dict:
                tmp_dict = {}
                for data_name in data.keys():
                    tmp_dict[data_name] = get_data(data[data_name])
                return tmp_dict
            raise ValueError("No data type fit for {}".format(data))

        for data_name in _data.keys():
            d = get_data(_data[data_name])
            # print(d)
            setattr(_object, data_name, d)
