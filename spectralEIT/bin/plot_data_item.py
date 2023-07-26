import pyqtgraph as pg
import numpy as np

class PlotDataItem(pg.PlotDataItem):

    def __init__(self, _list, _parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_text = self.text()

        self.parent_list = _list
        self.parent_item = _parent

        self.x_peaks = np.array([])
        self.y_peaks = np.array([])

        self.setCurveClickable(True)

    def text(self):
        return self.name()