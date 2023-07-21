import numpy as np

import yaml

class Constants():

    def __init__(self):

        _dict = yaml.safe_load( open("data/config/constants.yaml", 'r'))
        for key in _dict.keys():
            setattr(self, key, _dict[key])

        self.mu0 = 4 * np.pi * 1e-7 # magnetic field constant
        self.ep0 = 1 / (self.mu0 * self.c0 ** 2) # elektric field constant

        self.circ = 2 * np.pi

constants = Constants()
