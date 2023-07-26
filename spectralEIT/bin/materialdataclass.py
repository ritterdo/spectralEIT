from dataclasses import dataclass

import numpy as np

from spectralEIT.bin.constants import constants as con
from spectralEIT.bin.custom_yaml import YamlImport

class MaterialDataClass(YamlImport):

    expected_params = [
            "m0", "I", "number_density", "wavelength", "lifetime",
            "groundstate_frequencies", "excitedstate_frequencies", "dFactor"
        ]
    
    def __init__(self, name: str, _dict: dict):
        if not self.check_params(_dict):
            raise ValueError("Please check Yaml-file there is a problem with the parameters")
        self.set_attributes(_dict)
        tmp_array = []      
        for g_freq in self.groundstate_frequencies:
            for e_freq in self.excitedstate_frequencies:
                tmp_array.append(g_freq + e_freq)
        tmp_array = np.sort(np.array(tmp_array))
        if "Hf_config" in _dict.keys():
            setattr(self, "Hf", tmp_array[(np.array(_dict["Hf_config"]))])
        else:
            setattr(self, "Hf", tmp_array)
        self.Hw = con.circ * self.Hf
        self.natGamma = 1/self.lifetime
        if "D2" in name:
            self.d02 = 0.5 * 3 * con.ep0 * con.hbar * self.wavelength**3 / (8 * np.pi**2 * self.lifetime) # considering the 2*(J+1)/(2*(2J'+1)) factor
        elif "D1" in name:
            self.d02 = 3 * con.ep0 * con.hbar * self.wavelength**3 / (8 * np.pi**2 * self.lifetime)
        else:
            raise ValueError("Something wrong in d02 calculation")
        self.transitions = self.EIT_config.keys()
        self.w0 = con.circ * con.c0/self.wavelength
        self.k0 =  con.circ/self.wavelength

    def check_params(self, _dict: dict):
        
        def checking(_dict: dict):
            par_list = _dict.keys()
            for element in self.expected_params:
                if element not in par_list:
                    return False
            return True
        
        expected_length = len(self.expected_params)
        actual_length = len(_dict)
        
        if expected_length > actual_length:
            return False
        return checking(_dict)