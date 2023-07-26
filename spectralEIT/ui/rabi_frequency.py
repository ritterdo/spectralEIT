from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint

import numpy as np

from spectralEIT.bin.constants import constants as con
from spectralEIT.bin.default_config import *

import spectralEIT.bin.string_manipulation as stringManipu


class RabiFrequencyWindow(QWidget, DefaultClass):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.load_ui("../tools/rabiFrequency.ui")

        self.pushButton_calculate.clicked.connect(self.calculate)
        self.pushButton_cancel.clicked.connect(self.close_window)

        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = self.pos()

        self.show()

    def calculate(self):

        try:
            power = float(self.textEdit_laserPower.toPlainText())
            self.textEdit_laserPower.setStyleSheet("background:white")
        except Exception:
            self.textEdit_laserPower.setStyleSheet("background:red")
            power = None
        try:
            width0 = float(self.textEdit_width0.toPlainText())
            self.textEdit_width0.setStyleSheet("background:white")
        except Exception:
            self.textEdit_width0.setStyleSheet("background:red")
            width0 = None
        try:
            transition = int(self.textEdit_transition.toPlainText())
            self.textEdit_transition.setStyleSheet("background:white")
        except Exception:
            self.textEdit_transition.setStyleSheet("background:red")
            transition = None

        if power and width0 and transition != None:
            self.textEdit_laserPower.setStyleSheet("background:white")
            self.textEdit_width0.setStyleSheet("background:white")
            self.textEdit_transition.setStyleSheet("background:white")
            self.result(power, width0, transition)


    def result(self, power, width0, transition):
        self.label_result.setText(stringManipu.format_float_to_scale(con.dFactor[transition]*con.d0/con.hbar/width0*np.sqrt(4*power/np.pi),3)+" Hz")


    def key_press_event(self, event):
        if event.key() == Qt.Key_Enter:
            self.calculate()


    def close_window(self):
        self.close()


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()


    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

def show():
    return RabiFrequencyWindow()
