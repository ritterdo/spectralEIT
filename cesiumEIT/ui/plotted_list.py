from cesiumEIT.bin.custom_list_widget import CustomListWidget
from cesiumEIT.bin.plotable_list_item import PlotableListItem

class PlottedList(CustomListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def add_item(self, item):
        new = PlotableListItem(item.parent_list, item.parent_item, item.name())
        self.addItem(new)