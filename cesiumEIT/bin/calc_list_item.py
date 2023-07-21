from cesiumEIT.bin.calculation import LightPropagation
from cesiumEIT.bin.data_list_item import DataListItem

import numpy as np

class CalcListItem(LightPropagation, DataListItem):

    def __init__(self, parameters, *args, **kwargs):
        LightPropagation.__init__(self, parameters)
        DataListItem.__init__(self, *args, **kwargs)

        self.list_name = "calc"

    def isActivated(self):
        self.listWidget().select_item(self)


    def update_plotable(self):
        f = getattr(self.par, "f", np.array([]))
        if any(f):
            for name in ["IoutW", "IinW", "TAbs", "chiShape"]:
                data = getattr(self, name, np.array([]))
                if any(data):
                    if type(data[0]) is not np.complex128:
                        self.add_plot_item(name, f, data)
                    else:
                        self.add_plot_item(name+"_real", f, np.real(data))
                        self.add_plot_item(name+"_imag", f, np.imag(data))


        t = getattr(self, "t", np.array([]))
        if any(t):
            for name in ["IoutT", "IinT"]:
                data = getattr(self, name, np.array([]))
                if any(data):
                    self.add_plot_item(name, t, data)

        data = getattr(self, "rabiFunction", np.array([]))
        z = getattr(self, "z", np.array([]))
        if any(data):
            self.add_plot_item("rabiFunction", z, data)