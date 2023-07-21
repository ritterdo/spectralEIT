from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint

from numpy import log10

import cesiumEIT.bin.string_manipulation as stringManipu
import cesiumEIT.bin.info_windows as info

from cesiumEIT.bin.default_config import *

import sys

class LossLcCalculator(QWidget, DefaultClass):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.load_ui("../bin/lossLcCalculator.ui")

        self.pushButton_calculate.clicked.connect(self.calculate)
        self.pushButton_cancel.clicked.connect(self.closeWindow)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = self.pos()

        self.show() 


    def calculate(self):
        try:
            try:
                input = float(self.textEdit_input.toPlainText())
                self.textEdit_input.setStyleSheet("background:white")
            except Exception:
                self.textEdit_input.setStyleSheet("background:red")
                input = None
            try:
                output = float(self.textEdit_output.toPlainText())
                self.textEdit_output.setStyleSheet("background:white")
            except Exception:
                self.textEdit_output.setStyleSheet("background:red")
                output = None
            try:
                length = float(self.textEdit_length.toPlainText())
                self.textEdit_length.setStyleSheet("background:white")
            except Exception:
                self.textEdit_length.setStyleSheet("background:red")
                length = None

            if input and output and length != None:
                self.textEdit_input.setStyleSheet("background:white")
                self.textEdit_output.setStyleSheet("background:white")
                self.textEdit_length.setStyleSheet("background:white")
                self.result(input, output, length)
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())


    def result(self, input, output, length):
        self.label_result.setText(stringManipu.format_float_to_scale(10/length*log10(output/input),5)+" dB/m")


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.calculate()


    def closeWindow(self):
        self.close()


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()


    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

def show():
    return LossLcCalculator()
