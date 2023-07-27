import yaml
import os
import logging
import json

import numpy as np

from spectralEIT.bin.exceptions import MaterialError

from spectralEIT.bin.constants import constants as con
from spectralEIT.bin.materialdataclass import MaterialDataClass


class Material():


    def __init__(self, material: str=""):

        self.logger = logging.getLogger(material)
        self.logger.info("Initiate material %s", material)

        if material == None or material == "":
           raise MaterialError("No material selected")

        if material + ".yaml" not in self.get_material_list():
           raise MaterialError("Material not found in material/data")

        data_dict = self.get_dict(material)

        self.logger.info("Material parameters: %s", json.dumps(data_dict) if data_dict is not None else {})
        
        #if self.check_params(self.data_dict):
        self.set_material(material, data_dict)
        self.create_Hf()

        self.logger.info("Material setup finished")
        # else:
        #     raise ValueError("yaml-file params do not match the expected parameters")


    def get_dict(self, material: str):
        ## working direction is ./cesiumEIT/
        return yaml.safe_load(open("data/materials/" + material + ".yaml"))


    def get_material_list(self):
        ## working direction is ./cesiumEIT/
        return os.listdir("data/materials/")


    def set_material(self, name: str, _dict: dict):

        self.mat_list = []

        for key in _dict.keys():
            self.mat_list.append(key)
            setattr(self, key, MaterialDataClass(name, _dict[key]))
    
    def create_Hf(self):
        tmp = np.array([])
        for item in self.mat_list:
            tmp = np.concatenate((tmp, getattr(self, item).Hf))
        self.Hf = np.sort(tmp)


        
