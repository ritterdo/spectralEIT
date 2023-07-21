from cesiumEIT.bin.custom_list_widget import CustomListWidget
from cesiumEIT.bin.plotable_list_item import PlotableListItem

class PlotableList(CustomListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def update(self, item):
        self.clear()
        self.add_item(item)


    def add_item(self, item):
        for plot in item.plotable:
            new = PlotableListItem(item.parent_list, item, plot.name())
            self.addItem(new)