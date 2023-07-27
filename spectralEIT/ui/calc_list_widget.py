from cesiumEIT.bin.custom_list_widget import CustomListWidget
from cesiumEIT.bin.calc_list_item import CalcListItem

class CalcListWidget(CustomListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, name=__name__, **kwargs)

        self.logger.info("Initiate CalcListWidget")

        self.ListItem = CalcListItem


    def select_item(self, item: CalcListItem):
        super().select_item(item)

        self.window().config_tab.load_parameters(par_dict = self.currentItem().parameter_dict)

        item.update_plotable()
        self.window().update_plotable(item)