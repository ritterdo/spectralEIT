import sys

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal

import spectralEIT.bin.info_windows as info
import spectralEIT.bin.string_manipulation as stringManipu

from spectralEIT.bin.constants import constants as con
from spectralEIT.bin.material import Material as mat
from spectralEIT.bin.default_config import DefaultClass

import numpy as np
import scipy.signal as sig

class PlotTab(QWidget, DefaultClass):

    sigSetPoints = pyqtSignal(str,list)

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        DefaultClass.__init__(self, __name__)

        self.logger.info("Initiate PlotTab")

        self.load_ui("graphTab.ui")

        self.pushButton_get_fwhm.clicked.connect(self.get_fwhm)

        self.textEdit_cutoff_height_fwhm.setText("0.02")
        self.textEdit_cutoff_height_properties.setText("0.2")
        self.textEdit_relative_distance.setText("0.3")

        def select_points(name):
            self.window().tab_graph_widget.currentWidget().enable_point_selection = True
            self.window().tab_graph_widget.currentWidget().selection = name
            self.window().tab_graph_widget.currentWidget().tab = self

        def select_area(name):
            self.window().tab_graph_widget.currentWidget().enable_area_selection = True
            self.window().tab_graph_widget.currentWidget().selection = name
            self.window().tab_graph_widget.currentWidget().tab = self

        def set_points(name, _data_list):
            data_list = []
            try:
                for num in _data_list:
                    f_min = np.amin(self.x)
                    f_max = np.amax(self.x)
                    tol = 0.1*f_max
                    if num < f_min:
                        num = f_min + tol
                    if num > f_max:
                        num = f_max - tol
                    data_list.append(num)
                getattr(self, "textEdit_"+name).setText(stringManipu.format_float_to_scale(data_list, 2))
            except Exception:
                info.showCriticalErrorBox(sys.exc_info())

        self.pushButton_select_area.clicked.connect(lambda: select_area("select_area"))
        self.sigSetPoints.connect(set_points)
        self.import_material()


    def set_current_plot_item(self, plot_item):
        self.plot_item = plot_item
        self.x = self.plot_item.getData()[0]
        self.y = self.plot_item.getData()[1]
        self.textEdit_current_plot_item.setText(plot_item.name())

        self.set_peaks()
        self.window().tabWidget.setCurrentWidget(self)


    def get_peaks(self):

        self.logger.info("Get peaks")

        ratio = self.x.size/(np.max(self.x) - np.min(self.x))
        diff =  np.abs(np.max(self.y) - np.min(self.y))

        peaks, _ = sig.find_peaks(-(self.y-1), height=float(self.textEdit_cutoff_height_properties.toPlainText())*diff, distance=int(ratio*1e9))

        self.plot_item.x_peaks = self.x[peaks]
        self.plot_item.y_peaks = self.y[peaks]


    def set_peaks(self):

        self.logger.info("Set peaks")

        try:
            ## Select material
            material = mat(self.comboBox_material.currentText())

            if not any(self.plot_item.x_peaks):
                self.get_peaks()

            frame = self.scroll_plot_properties
            layout = frame.layout()
            if not layout:
                layout = QGridLayout()
                frame.setLayout(layout)
            else:
                for i in reversed(range(2,layout.count())):
                    layout.itemAt(i).widget().setParent(None)

            style =  "border: 1px solid #76797C;"
            textEditStyle = "background-color: #232629; color: #eff0f1;"

            label = QLabel("Theoretical")
            label.setStyleSheet(style)
            layout.addWidget(label, 0, 1)

            label = QLabel("From Plot")
            label.setStyleSheet(style)
            layout.addWidget(label, 0, 2)

            for i in range(self.plot_item.x_peaks.size):

                self.logger.info("Add peak %d to plot properties", i+1)

                label = QLabel("x"+str(i+1))
                label.setStyleSheet(style)
                layout.addWidget(label, i+1, 0)

                label = QLabel(stringManipu.format_float_to_scale(material.Hf[i], 2))
                label.setStyleSheet(style+textEditStyle)
                layout.addWidget(label, i+1, 1)

                label = QLabel(stringManipu.format_float_to_scale(self.plot_item.x_peaks[i], 2))
                label.setStyleSheet(style+textEditStyle)
                layout.addWidget(label, i+1, 2)
                if i+1 == self.plot_item.x_peaks.size:
                    button = QPushButton("Show")
                    button.clicked.connect(self.show_theoretical_peaks)
                    layout.addWidget(button, i+2, 1)

                    button = QPushButton("Show")
                    button.clicked.connect(self.show_experimental_peaks)
                    layout.addWidget(button, i+2, 2)
        except Exception as e:
            info.showCriticalErrorBox(sys.exc_info())
            return
            

    def show_experimental_peaks(self):

        self.logger.info("Show experimental peaks")

        if not any(self.plot_item.x_peaks):
            self.get_peaks()
        
        self.window().tab_graph_widget.currentWidget().remove_peak_lines("experimental")

        for i, x in enumerate(self.plot_item.x_peaks):
            self.window().tab_graph_widget.currentWidget().add_peak_line(x, number=i, name="experimental", color="red")


    def show_theoretical_peaks(self):

        self.logger.info("Show theoretical peaks")

        ## Select material
        material = mat(self.comboBox_material.currentText())

        self.window().tab_graph_widget.currentWidget().remove_peak_lines("theoretical")

        for i, x in enumerate(material.Hf):
            self.window().tab_graph_widget.currentWidget().add_peak_line(x, number=i, name="theoretical", color="green")


    def get_fwhm(self):

        self.logger.info("Get FWHM")

        ## Select material
        material = mat(self.comboBox_material.currentText())

        ## Full Width Half Maximum of a x and a corresponding y
        def FWHM(x, y, height=None, inverted=False, distance=None):

            if inverted:
                self.logger.info("Invert y in FWHM")
                y = -1*(y-1)

            peaks,_ = sig.find_peaks(y, height=height, distance=distance)
            fwhm, fwhm_heights, left, right = sig.peak_widths(y,peaks)

            length = len(fwhm)
            widths = np.zeros(length)

            for i in range(length):
                widths[i] = np.abs(x[int(right[i])] - x[int(left[i])])

            if length == 1:
                return peaks[0], widths[0], left[0], right[0]
            return peaks, widths, left, right

        area = self.textEdit_select_area.toPlainText()
        if area == "":
            x_area = self.x
            y_area = self.y
        else:
            area = np.float32(np.array(area.split(",")))
            x_area = self.x[(area[0]<self.x)&(self.x<area[1])]
            y_area = self.y[(area[0]<self.x)&(self.x<area[1])]

        distance = float(self.textEdit_relative_distance.toPlainText())*x_area.size/(np.max(x_area)-np.min(x_area))*np.abs(material.Hf[1]-material.Hf[0])

        self.logger.info("Distance: %f", distance)

        peaks, widths, left, right = FWHM(x_area, y_area, height=float(self.textEdit_cutoff_height_fwhm.toPlainText())*np.max(y_area), inverted=self.checkBox_inverted_peak.isChecked(), distance=distance)

        self.logger.info("Peaks in indices: %s", str(peaks))
        self.logger.info("Peaks in frequency: %s", str(x_area[peaks]))
        self.logger.info("Widths: %s", str(widths))
        self.logger.info("Left in indices: %s", str(left))
        self.logger.info("Left in frequency (rounded): %s", str(x_area[left.round().astype(int)]))
        self.logger.info("Right in indices: %s", str(right))
        self.logger.info("Right in frequency (rounded): %s", str(x_area[right.round().astype(int)]))

        self.logger.info("Write to textEdit in FWHM")
        self.textEdit_x.setText(stringManipu.format_float_to_scale(x_area[peaks], 2))
        self.textEdit_y.setText(stringManipu.format_float_to_scale(y_area[peaks], 2))
        self.textEdit_widths.setText(stringManipu.format_float_to_scale(widths, 2))

        self.logger.info("Add FWHM to plot")
        self.window().tab_graph_widget.currentWidget().add_fwhm_line(x_area[left.round().astype(int)], x_area[right.round().astype(int)], y_area[right.round().astype(int)])
