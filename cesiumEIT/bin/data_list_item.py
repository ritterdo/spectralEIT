from cesiumEIT.bin.custom_list_item import CustomListItem
from cesiumEIT.bin.plot_data_item import PlotDataItem

class DataListItem(CustomListItem):

    def __init__(self, _parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent_list = _parent

        self.plotable = []
        self.plotable_names = []


    def add_plot_item(self, name, x, y):
        name = self.text() + "_" + name
        if name in self.plotable_names:
            getattr(self, name).setData(x,y)
            return
        else:
            setattr(self, name, PlotDataItem(self.parent_list, self, x, y, name=name, antialias=True))
            self.plotable.append(getattr(self, name))
            self.plotable_names.append(name)