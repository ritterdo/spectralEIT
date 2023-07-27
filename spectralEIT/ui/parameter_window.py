from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QGridLayout, QLabel
from PyQt5.QtCore import Qt


import cesiumEIT.bin.info_windows as info
import cesiumEIT.bin.string_manipulation as stringManipu

class ParameterWindow(QWidget):

    def __init__(self, parameters):
        super(ParameterWindow, self).__init__()

        if parameters:
            self.allParDict = parameters
        else:
            info.showInfoBox("Nothing was calculated yet. All parameters are the default values.")
            return

        self.vbox = QGridLayout()
        self.setWindowTitle("Parameter Window")

        self.set_data()

        pushButton_close = QPushButton("Cancel")
        pushButton_close.setGeometry(0,0,75,30)
        self.vbox.addWidget(pushButton_close)
        pushButton_close.clicked.connect(self.close)

        self.show()

    def set_data(self):

        for setNumber in self.allParDict.keys():

            table = QTableWidget(self)
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Name","Value"])
            hheader = table.horizontalHeader()
            hheader.setSectionResizeMode(QHeaderView.Stretch)

            title = QLabel()
            title.setText("Set " + str(setNumber + 1))

            # rowNumbers = len(self.allParDict[setNumber].keys()) + 1
            table.setRowCount(len(self.allParDict[setNumber].keys()))

            # table.setItem(0,0, QTableWidgetItem("SetNumber"))
            # value = QTableWidgetItem(str(setNumber+1))
            # value.setTextAlignment(Qt.AlignRight)
            # table.setItem(0,1, value)

            for row, names in enumerate(self.allParDict[setNumber].keys()):
                newName = QTableWidgetItem(names)
                newValue = QTableWidgetItem(self.allParDict[setNumber][names] if type(self.allParDict[setNumber][names]) is str else stringManipu.format_float_to_scale(self.allParDict[setNumber][names]))
                newValue.setTextAlignment(Qt.AlignRight)
                table.setItem(row, 0, newName)
                table.setItem(row, 1, newValue)

            self.vbox.addWidget(title, 0, int(setNumber))
            self.vbox.addWidget(table, 1, int(setNumber))

        self.setLayout(self.vbox)


def show(parDicts):

    return ParameterWindow(parDicts)
