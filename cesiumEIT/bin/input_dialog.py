from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QLabel
from PyQt5.QtCore import Qt

class DoubleInputDialog(QDialog):
    def __init__(self, parent=None,title="", label1="First text", label2="Second text"):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        title = QLabel(title, self)
        layout = QFormLayout(self)
        layout.addWidget(title)
        layout.addRow(label1, self.first)
        layout.addRow(label2, self.second)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def get_inputs(self):
        return self.first.text(), self.second.text()
