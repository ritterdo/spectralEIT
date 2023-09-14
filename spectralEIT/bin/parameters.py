import numpy as np

import os
import yaml

from spectralEIT.bin.constants import constants as con
from spectralEIT.bin.default_parameters import DEFAULT_PARAMETER_DICT

from spectralEIT.bin.custom_yaml import YamlImport

class Parameters(YamlImport):

    def __init__(self, parameters: dict=None):

        self.set_parameters(parameters)


    def set_parameters(self, _dict: dict=None):

        keys = _dict.keys()
        if _dict == None:
            self.set_attributes(DEFAULT_PARAMETER_DICT)
        else:
            tmp_dict = {}
            for par in DEFAULT_PARAMETER_DICT.keys():
                if par in keys:
                    tmp_dict[par] = _dict[par]
                else:
                    tmp_dict[par] = DEFAULT_PARAMETER_DICT[par]
            self.set_attributes(tmp_dict)

        self.f = np.linspace(self.freqStart, self.freqStop, int(self.freqSteps))

        self.gridSize = len(self.f)
        self.w0Det,self.wDet,self.gammadCirc,self.EITDetuneCirc = con.circ*np.array([self.f0det,self.f,self.gammad,self.EITDetune],dtype=object)
        self.Tk = 273.15 + self.T
