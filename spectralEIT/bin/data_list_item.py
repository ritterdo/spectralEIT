from spectralEIT.bin.custom_list_item import CustomListItem
from spectralEIT.bin.plot_data_item import PlotDataItem

import logging

class DataListItem(CustomListItem):

    def __init__(self, _parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger(__name__)

        self.parent_list = _parent

        self.plotable = []
        self.plotable_names = []


    def add_plot_item(self, name, x, y):
        name = self.text() + "_" + name
        self.logger.info("Add Plot Item: %s",name)
        if name in self.plotable_names:
            self.logger.info("Updating data for: %s", name)
            getattr(self, name).setData(x,y)
        else:
            setattr(self, name, PlotDataItem(self.parent_list, self, x, y, name=name, antialias=True))
            self.plotable.append(getattr(self, name))
            self.plotable_names.append(name)
            self.logger.info("Plotable: %s", self.plotable_names)
                        
    
    def remove_plot_item(self, name):
        name = self.text() + "_" + name
        self.logger.info("Remove Plot Item: %s",name)
        if name in self.plotable_names:
            self.plotable.remove(getattr(self, name))
            self.plotable_names.remove(name)
            delattr(self, name)
            self.logger.info("Plotable: %s", self.plotable_names)
        else:
            self.logger.info("Item not in plotable list: %s", name)
            self.logger.info("Plotable: %s", self.plotable_names)