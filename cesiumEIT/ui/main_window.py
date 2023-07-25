from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox
from PyQt5.QtCore import QThreadPool, Qt, pyqtSignal, QPoint

import re

import cesiumEIT.ui.loss_lc_calculator as lossWin
import cesiumEIT.ui.rabi_frequency as rabiWin

import cesiumEIT.bin.info_windows as info
import cesiumEIT.bin.input_dialog as input
import cesiumEIT.bin.parameters as par

from cesiumEIT.bin.default_parameters import DEFAULT_PARAMETER_DICT
from cesiumEIT.bin.default_config import DefaultClass

class MainWindow(QMainWindow, DefaultClass):

    ##
    ## UI Setup
    ##

    plot_tab_changed = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        DefaultClass.__init__(self, __name__)

        self.logger.info("Initiate MainWindow")

        self.set_window_properties()

        # Setup threading for calculation
        self.threadpool = QThreadPool()
        self.threadIsRunning = {}

        self.set_statusbar()

        ## Activate first tab as default
        self.tabWidget.setCurrentIndex(0)
        self.tab_graph_widget.setCurrentIndex(0)
        self.plot_tab_changed.connect(self._plot_tab_changed)

        self.init_menu()

        ## Set buttons and Lists
        def calc_list_add_item():
            self.calc_list.add_item(_parent = self.calc_list, parameters = DEFAULT_PARAMETER_DICT, item_name="calc")
            self.tabWidget.setCurrentIndex(0)

        self.pushButton_calc_list_add.clicked.connect(calc_list_add_item)
        self.pushButton_calc_list_del.clicked.connect(self.calc_list.del_item)

        def meas_list_add_item():
            self.meas_list.add_item(_parent = self.meas_list, material = self.meas_tab.comboBox_material.currentText(), item_name="meas")
            self.tabWidget.setCurrentIndex(1)

        self.pushButton_meas_list_add.clicked.connect(meas_list_add_item)
        self.pushButton_meas_list_del.clicked.connect(self.meas_list.del_item)

        self.pushButton_plot_add.clicked.connect(self.add_plot)
        self.pushButton_plot_del.clicked.connect(self.del_plot)

        ## Plot Widget Buttons
        self.pushButton_remove_lines.clicked.connect(self.remove_lines)
        self.pushButton_axis_label.clicked.connect(self.add_axis_labels)

        # Initialize window variables
        self.init_windows()

        self.logger.info("MainWindow successfully initiated")


    def set_window_properties(self):

        self.logger.info("Set MainWindow properties")

        self.load_ui("mainWindow.ui")
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = self.pos()
        self.moveWindow = False


    def set_statusbar(self):

        self.logger.info("Set MainWindow statusbar")

        self.statusbarMessage = QLabel()
        self.statusbarMessage.setText("Ready")
        version = QLabel()
        version.setText(open("version.txt", "r").read())

        self.statusbar.addPermanentWidget(self.statusbarMessage)
        self.statusbar.addWidget(version)


    def init_menu(self):

        self.logger.info("Initiate MainWindow menu bar")

        ## Setup menu bar
        self.actionRabi_Frequency_Calculator.triggered.connect(self.show_rabi_calculator)
        self.actionLoss_LC_Calculator.triggered.connect(self.show_loss_lc_calculator)
        self.actionClose.triggered.connect(self.close)


    def init_windows(self):

        self.lossWindow = None
        self.rabiWindow = None

        self.peaks_area = {1:"", 2:""}


    ## Close Function
    def closeEvent(self,event):

        self.logger.info("Initate closing sequence")
        result = info.showQuestionBox("Confirm Exit...", "Are you sure you want to exit?")

        event.ignore()

        if result == QMessageBox.Yes:
            if self.rabiWindow:
                self.rabiWindow.close()
            if self.lossWindow:
                self.lossWindow.close()

            self.logger.info("Closing Application")
            
            event.accept()


    def show_rabi_calculator(self):
        if self.rabiWindow:
            self.parWindow.close()
        self.rabiWindow = rabiWin.show()


    def show_loss_lc_calculator(self):
        if self.lossWindow:
            self.lossWindow.close()
        self.lossWindow = lossWin.show()


    def update_plotted_list(self, list: list):
        self.plotted_list.clear()
        self.logger.info("Plotted list changed to: " + "".join(item.name() for item in list))
        for item in list:
            print(item.name())
            self.plotted_list.add_item(item)


    def update_plotable(self, item):
        self.plotable_list.update(item)


    def add_axis_labels(self):
        dialog = input.DoubleInputDialog(label1="x Axis", label2="y Axis", title="Set Axis Labels")
        if dialog.exec_():
            x_axis_label, y_axis_label = dialog.get_inputs()
            plot_widget = self.tab_graph_widget.currentWidget()
            if x_axis_label:
                match = re.findall(r"([a-zA-Z\s]*)[\[(a-zA-Z*)\]]?", x_axis_label)
                plot_widget.setLabel(axis="bottom", text=match[0], units=match[1])
            if y_axis_label:
                match = re.findall(r"([a-zA-Z\s]*)[\[(a-zA-Z*)\]]?", y_axis_label)
                plot_widget.setLabel(axis="left", text=match[0], units=match[1])


    def _plot_tab_changed(self, index):
        tab = self.tab_graph_widget.widget(index)
        self.logger.info("Graph tab changed to %s", self.tab_graph_widget.tabText(index))
        self.update_plotted_list(tab.plotted.values())


    def add_plot(self):
        item = self.plotable_list.currentItem()
        plot = getattr(item.parent_item, item.text())
        self.tab_graph_widget.currentWidget().add_item(plot)


    def del_plot(self):
        item = self.plotted_list.currentItem()
        plot = getattr(item.parent_item, item.text())
        self.tab_graph_widget.currentWidget().del_item(plot, item)


    def remove_lines(self):
        self.tab_graph_widget.currentWidget().remove_lines()


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
        if not self.tab_graph_widget.geometry().contains(event.globalPos()):
            self.moveWindow = True
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self.moveWindow == True:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        if self.moveWindow == True:
            self.moveWindow = False
        super().mouseReleaseEvent(event)
