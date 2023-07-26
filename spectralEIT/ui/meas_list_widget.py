from cesiumEIT.bin.custom_list_widget import CustomListWidget
from cesiumEIT.bin.meas_list_item import MeasListItem

class MeasListWidget(CustomListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ListItem = MeasListItem


    def select_item(self, item: MeasListItem):
        super().select_item(item)

        self.window().meas_tab.set_current_import(item)
        self.window().meas_tab.textEdit_file_name.setText(item.file_name)
        item.update_plotable()
        self.window().update_plotable(item)