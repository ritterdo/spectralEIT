from spectralEIT.bin.custom_list_item import CustomListItem

class PlotableListItem(CustomListItem):


    def __init__(self, parent_list, parent_item, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent_list = parent_list
        self.parent_item = parent_item