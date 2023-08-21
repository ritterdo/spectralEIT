from spectralEIT.bin.measurement import Measurements
from spectralEIT.bin.data_list_item import DataListItem

from PyQt5.QtCore import pyqtSignal

class MeasListItem(Measurements, DataListItem):

    sigUpdatePlotable = pyqtSignal(bool)

    def __init__(self, *args, material,  **kwargs):
        Measurements.__init__(self, material)
        DataListItem.__init__(self, *args, **kwargs)

        self.list_name = "meas"

        # self.update_plotable()

    def update_item(self, checkBox_debug_graphs = False):
        self.update_plotable(checkBox_debug_graphs)

    def isActivated(self):
        self.listWidget().select_item(self)

    def update_plotable(self, checkBox_debug_graphs = False):

        freq = self.values[0]
        self.add_plot_item("Refrenece_Original", freq, self.values[1])
        self.add_plot_item("Spectrum_Original", freq, self.values[2])

        ## Set Manipulated Data
        self.add_plot_item("Reference", self.frequency, self.reference)
        self.add_plot_item("Spectrum", self.frequency, self.spectrum)

        ## Set Subsampled Data
        if hasattr(self, "f_sub"):
            self.add_plot_item("Spectrum_Subsampled", self.f_sub, self.spectrum_sub)
        
        if checkBox_debug_graphs:
            # Debug Graphs
            # background removal baseline
            if hasattr(self, "background_spectrum"):
                self.add_plot_item("Background_Spectrum", self.frequency, self.background_spectrum)
                
            if hasattr(self, "background_reference"):
                self.add_plot_item("Background_Reference", self.frequency, self.background_reference)
                
            if hasattr(self, "inverse_spectrum"):
                self.add_plot_item("inverse_Spectrum", self.frequency, self.inverse_spectrum)
                
            if hasattr(self, "inverse_reference"):
                self.add_plot_item("inverse_Reference", self.frequency, self.inverse_reference)

            # background removal polyfit
            if hasattr(self, "background_polyfit_spectrum"):
                self.add_plot_item("Background_Spectrum", freq, self.background_polyfit_spectrum)
                
            if hasattr(self, "background_polyfit_reference"):
                self.add_plot_item("Background_Reference", freq, self.background_polyfit_reference)

            # volt to frequency conversion
            if hasattr(self, "debug_reffit_freq"):
                self.add_plot_item("debug_reffit_freq", self.frequency, self.debug_reffit_freq)
            
            if hasattr(self, "initial_reffit_freq"):
                self.add_plot_item("initial_reffit", self.frequency, self.initial_reffit_freq)
            
        else:
            if hasattr(self, "background_spectrum"):
                self.remove_plot_item("Background_Spectrum")
                
            if hasattr(self, "background_reference"):
                self.remove_plot_item("Background_Reference")
                
            if hasattr(self, "inverse_spectrum"):
                self.remove_plot_item("inverse_Spectrum")
                
            if hasattr(self, "inverse_reference"):
                self.remove_plot_item("inverse_Reference")

            if hasattr(self, "background_polyfit_spectrum"):
                self.remove_plot_item("Background_Spectrum")
                
            if hasattr(self, "background_polyfit_reference"):
                self.remove_plot_item("Background_Reference")
        
            if hasattr(self, "debug_reffit_freq"):
                self.remove_plot_item("debug_reffit_freq")
            
            if hasattr(self, "initial_reffit_freq"):
                self.remove_plot_item("initial_reffit",)

        