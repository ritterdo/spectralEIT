from spectralEIT.bin.measurement import Measurements
from spectralEIT.bin.data_list_item import DataListItem

class MeasListItem(Measurements, DataListItem):

    def __init__(self, *args, material,  **kwargs):
        Measurements.__init__(self, material)
        DataListItem.__init__(self, *args, **kwargs)

        self.list_name = "meas"

        # self.update_plotable()

    def update_item(self):
        self.update_plotable()

    def isActivated(self):
        self.listWidget().select_item(self)

    def update_plotable(self):

        freq = self.values[0]
        self.add_plot_item("Refrenece_Original", freq, self.values[1])
        self.add_plot_item("Spectrum_Original", freq, self.values[2])

        ## Set Manipulated Data
        self.add_plot_item("Reference", self.frequency, self.reference)
        self.add_plot_item("Spectrum", self.frequency, self.spectrum)

        ## Set Subsampled Data
        if hasattr(self, "f_sub"):
            self.add_plot_item("Spectrum_Subsampled", self.f_sub, self.spectrum_sub)
           
        if hasattr(self, "background_spectrum"):
            self.add_plot_item("Background_Spectrum", self.frequency, self.background_spectrum)
            
        if hasattr(self, "background_reference"):
            self.add_plot_item("Background_Reference", self.frequency, self.background_reference)
            
        if hasattr(self, "inverse_spectrum"):
            self.add_plot_item("inverse_Spectrum", self.frequency, self.inverse_spectrum)
            
        if hasattr(self, "inverse_reference"):
            self.add_plot_item("inverse_Reference", self.frequency, self.inverse_reference)
        