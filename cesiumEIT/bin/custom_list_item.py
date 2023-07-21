from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import Qt

class CustomListItem(QListWidgetItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_text = self.text()

        self.setFlags(self.flags() | Qt.ItemIsEditable)