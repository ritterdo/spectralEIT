from PyQt5.QtWidgets import QListWidget

class CustomListWidget(QListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.list_names = []

        self.ListItem = None
        self.plotable = []

        self.itemClicked.connect(self.select_item)
        self.itemChanged.connect(self.select_item)

        self.setSortingEnabled(True)


    def del_item(self):
        self.list_names.remove(self.currentItem().text())
        self.takeItem(self.indexFromItem(self.currentItem()).row())


    def get_item(self, name: str):
        for i in range(self.count()):
            item = self.item(i)
            if name == item.text():
                return item
        return None


    def add_item(self, *args, item_name: str = "new", i: int = 0, item = None, **kwargs):
        tmp_name = item_name + "_{}".format(i) if i !=0 else item_name
        if tmp_name in self.list_names:
            self.add_item(*args, item_name=item_name, i=i+1, **kwargs)
        else:
            self.list_names.append(tmp_name)
            if item == None:
                tmp = self.ListItem(*args, **kwargs)
                tmp.setText(tmp_name)
            else:
                tmp = item
            self.addItem(tmp)
            self.setCurrentItem(tmp)
            tmp.isActivated()
        return

    def select_item(self, item):
        self.window().config_tab.refresh_ui()