import numpy as np

import logging

from os import path, listdir, getcwd
from PyQt5 import uic
from platform import system

ui_path = path.join(*list(path.split(getcwd())) + ["ui"])


class DefaultClass:

    def __init__(self, name:str = __name__):
        self.logger = logging.getLogger(name)
        self.logger.debug("Initiate %s logger", name)

    def load_ui(self, name: str):
        assert name.endswith(".ui")
        uic.loadUi(path.join(ui_path, system() + '_' + name), self)


    def import_material(self):

        material_list = [ x.split(".")[0] for x in listdir("data/materials") ]

        if "cesium_D1" not in material_list:
            raise ImportError("Could not get default material: cesium_D1")

        for material in material_list:
            name_list = [self.comboBox_material.itemText(i) for i in range(self.comboBox_material.count())]
            self.comboBox_material.addItem(material)
        self.comboBox_material.setCurrentText("cesium_D1")


PLOT_PARAMS = ["IoutT", "IinT", "IoutW", "IinW", "TAbs", "rabiFunction"]
PLOT_LEGEND = {keys: value+" Set {}" for key, value in [(["IoutT", "IoutW"],"Output Intensity"), (["IinT", "IinW"], "Input Intensity"), (["TAbs"], "Transferfunction"), (["rabiFunction"], "Rabi Frequency"), (["measurement"], "Measurement")] for keys in key}
MEASUREMENT_PAR = ["main_area", "peaks_area_1", "peaks_area_2", "polyfit_degree", "ref_heights", "ref_peaks", "sampling_steps", "flim", "EIT_transition", "EIT_range_tolerance"]


PAR_LIST_FIT = [
        "rabiFrequency",
        "lossdB",
        "width0",
        "focalLength",
        "posLC",
        "cellLength",
        "dt",
        "pulseFreq",
        "lcLength",
        "EITDetune",
        "f0det",
        "gammad",
        "gamma_coll",
        "gamma_power",
        "T"
    ]


PAR_DICT_INT_TYPE = [
        "transition",
        "zsteps"
    ]


LIST_TYPES = [np.ndarray,np.array,list]
NUMBER_TYPES  = [np.int32,np.float32,np.int64,np.float64,int,float]


COLOUR_MAP = {
        0:"#1f77b4",
        1:"#ff7f0e",
        2:"#2ca02c",
        3:"#d62728",
        4:"#9467bd",
        5:"#8c564b",
        6:"#e377c2",
        7:"#7f7f7f",
        8:"#bcbd22",
        9:"#17becf"
    }
