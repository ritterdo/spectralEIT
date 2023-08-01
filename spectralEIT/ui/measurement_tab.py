import sys
import os

import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

import spectralEIT.bin.info_windows as info
import spectralEIT.bin.string_manipulation as stringManipu

from spectralEIT.bin.default_config import DefaultClass
from spectralEIT.bin.exceptions import InputError

class MeasurementTab(QWidget, DefaultClass):

    sigSetPoints = pyqtSignal(str,list)

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        DefaultClass.__init__(self, __name__)

        self.logger.info("Initiate MeasurementTab")

        self.load_ui("measurementTab.ui")

        self.pushButton_modify_x.clicked.connect(self.modify_x)
        self.pushButton_reset_measurement.clicked.connect(self.reset_data)
        self.pushButton_inverse_measurement.clicked.connect(self.inverse_data)
        self.pushButton_remove_background.clicked.connect(self.remove_background)
        self.pushButton_subsampling.clicked.connect(self.subsampling)
        self.pushButton_initial_cut.clicked.connect(self.initial_cut)
        self.pushButton_perform_all.clicked.connect(self.perform_all)

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
                    f_min = np.amin(self.current_import.frequency)
                    f_max = np.amax(self.current_import.frequency)
                    tol = 0.1*f_max
                    if num < f_min:
                        num = f_min + tol
                    if num > f_max:
                        num = f_max - tol
                    data_list.append(num)
                getattr(self, "textEdit_"+name).setText(stringManipu.format_float_to_scale(data_list, 2))
            except Exception:
                info.showCriticalErrorBox(sys.exc_info())


        self.pushButton_main_area.clicked.connect(lambda: select_area("main_area"))
        self.pushButton_peaks_area_1.clicked.connect(lambda: select_area("peaks_area_1"))
        self.pushButton_peaks_area_2.clicked.connect(lambda: select_area("peaks_area_2"))
        self.pushButton_sampling_area.clicked.connect(lambda: select_area("sampling_area"))
        self.pushButton_highres_area.clicked.connect(lambda: select_area("highres_area"))
        self.pushButton_ref_peaks.clicked.connect(lambda: select_points("ref_peaks"))

        self.sigSetPoints.connect(set_points)

        self.set_default_values()
        self.setup_tool_tips()
        self.import_material()


    def set_current_import(self, item):
        self.current_import = item
        self.logger.info("Set current_import to %s", item.text())


    def set_default_values(self):

        ## set measurement default parameters
        self.textEdit_polyfit_degree_background.setText("8")
        self.textEdit_polyfit_degree_peaks.setText("2")
        self.textEdit_sampling_steps.setText("10")
        self.textEdit_ref_heights.setText("0.4,0.3,0.2,0.4")


    def setup_tool_tips(self):

        # Measurement Tab
        self.pushButton_inverse_measurement.setToolTip("Inverse Measurement")
        self.pushButton_modify_x.setToolTip("Scale measurement axis to frequency axis.\nUser Input:\n - Approximate Doppler free peak positions\n - Approximate peak heights")
        self.pushButton_remove_background.setToolTip("Remove Background/Straighten the measurement\nUser Input:\n - Degree of fit polynomial, Default: 8\n - Cut out area of the peaks (two areas)")
        self.pushButton_subsampling.setToolTip("Reduce sample size outside of EIT area.\nUser Input:\n - EIT transition\n - Frequency Limit in Hz\n - Subsamplesize, Default: 10\n - EIT range tolerance in Hz, Default: 1e9 [Hz]")
        self.label_polyfit_degree_background.setToolTip("Select degree of fit polynomial for the background removal, Default: 8")
        self.label_ref_peak_positions.setToolTip("Select four approximate peak positions in reference measurement.\nExample: -.75,-.6,.56,.75 [Volt]")
        self.label_ref_peak_heights.setToolTip("Select fout approximate peak heights in reference measurement.\nExample: 0.2,0.1,0.3,0.4")
        self.label_polyfit_degree_peaks.setToolTip("Select degree of fit polynomial for the voltage to frequency conversion, Default: 2")


    def inverse_data(self) -> None:
        self.logger.info("Inverse the data of %s", self.current_import.text())
        try:
            if self.current_import.reference.any():
                self.current_import.reference = self.current_import.inverse_value(self.current_import.reference)
            if self.current_import.spectrum.any():
                self.current_import.spectrum = self.current_import.inverse_value(self.current_import.spectrum)
            self.current_import.update_item()
            self.logger.info("Inversion successful")
            return None
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())
            return None


    def initial_cut(self) -> None:
        self.logger.info("Inital cut/Main area cut out of %s", self.current_import.text())
        try:
            cut_str = self.textEdit_main_area.toPlainText()
            if cut_str == "":
                info.showCriticalMessageBox("Please select an area!")
                return None
            else:
                main_area = np.array([float(x) for x in cut_str.split(",")])
            if self.current_import.reference.any():
                self.current_import.reference = self.current_import.initial_cut(self.current_import.reference, cut = main_area)
            if self.current_import.spectrum.any():
                self.current_import.spectrum = self.current_import.initial_cut(self.current_import.spectrum, cut = main_area)
            if self.current_import.frequency.any():
                self.current_import.frequency = self.current_import.initial_cut(self.current_import.frequency, cut = main_area)
            self.current_import.update_item()
            self.logger.info("Initial cut/Main area cut out successful")
            return None
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())
            return None


    def reset_data(self) -> None:
        self.logger.info("Reset data for %s", self.current_import.text())
        try:
            self.current_import.set_data()
            self.current_import.update_item()
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())
            return


    def modify_x(self) -> None:
        self.logger.info("Modify X from Volt to frequency for %s", self.current_import.text())
        try:
            initial_guess = {"initial_offset_x":np.array([float(x) for x in self.textEdit_ref_peaks.toPlainText().split(",")]),
                "initial_offset_y":0,
                "initial_amps":np.array([float(x) for x in self.textEdit_ref_heights.toPlainText().split(",")]),
                "initial_widths":np.ones(4)*0.5
                }
            self.current_import.frequency = self.current_import.modify_X(self.current_import.frequency,self.current_import.reference,polyfit_degree=int(self.textEdit_polyfit_degree_peaks.toPlainText()),**initial_guess)
            self.current_import.update_item()
            self.window().update_plotable(self.current_import)

            self.window().tab_graph_widget.currentWidget().remove_selection_lines()
            self.logger.info("Modification successful")
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())
            return


    def remove_background(self) -> None:
        self.logger.info("Removing background for %s", self.current_import.text())
        try:
            cut1 = self.textEdit_peaks_area_1.toPlainText()
            cut2 = self.textEdit_peaks_area_2.toPlainText()
            degree = int(self.textEdit_polyfit_degree_background.toPlainText())
            if cut1 == "":
                 raise InputError("Please enter the cut out 1 error\nExample: -0.7,-0.2")
            else:
                cut1 = np.float32(np.array(cut1.split(",")))
            if cut2 == "":
                raise InputError("Please enter the cut out 2 error\nExample: -0.7,-0.2")
            else:
               cut2 = np.float32(np.array(cut2.split(",")))

            background_args = { "cut1" : cut1,
                "cut2" : cut2,
                "polyfit_degree" : degree
                }
            self.current_import.reference = self.current_import.remove_background(self.current_import.frequency,self.current_import.reference, **background_args, set = "reference")
            self.current_import.spectrum = self.current_import.remove_background(self.current_import.frequency,self.current_import.spectrum, **background_args, set = "spectrum")
            # self.current_import.reference = self.current_import.remove_background(self.current_import.frequency,self.current_import.reference,set = "reference")
            # self.current_import.spectrum = self.current_import.remove_background(self.current_import.frequency,self.current_import.spectrum, set = "spectrum")
            self.current_import.update_item()
            self.window().update_plotable(self.current_import)
            self.logger.info("Removal successful")
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())
            return


    def subsampling(self):
        self.logger.info("Subsampling for %s", self.current_import.text())
        try:

            sample_area = self.textEdit_sampling_area.toPlainText()
            highres_area = self.textEdit_highres_area.toPlainText()
            sampling = self.textEdit_sampling_steps.toPlainText()

            if sample_area == "":
                x = np.array([])
                y = np.array([])
            else:
                sample_area = np.float32(np.array(sample_area.split(",")))
                x = self.current_import.frequency[(sample_area[0]<self.current_import.frequency)&(self.current_import.frequency<sample_area[1])]
                y = self.current_import.spectrum[(sample_area[0]<self.current_import.frequency)&(self.current_import.frequency<sample_area[1])]

            if highres_area == "":
                highres_area = []
            else:
                highres_area = np.float32(np.array(highres_area.split(",")))

            if sampling == "":
                sampling = 10
            else:
                sampling = int(sampling)
 
            self.logger.info("Sampling area: [%f,%f]", sample_area[0], sample_area[1])
            self.logger.info("High resolution area: [%f,%f]", highres_area[0], highres_area[1])
 
            self.current_import.f_sub,self.current_import.spectrum_sub = self.current_import.subsampling(x, y, highres_area, sampling)
            self.current_import.update_item()
            self.window().update_plotable(self.current_import)
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())
            return


    def perform_all(self) -> None:
        self.remove_background()
        self.modify_X()
        self.subsampling()
