import sys
import copy

from os import getcwd, path

import numpy as np

from pybaselines import Baseline

import spectralEIT.bin.auxiliary_func as aux
import spectralEIT.bin.info_windows as info

from spectralEIT.bin.constants import constants as con
from spectralEIT.bin.material import Material as mat
from spectralEIT.bin.data_io import DataIO
from spectralEIT.bin.exceptions import BackgroundRemoveError, SubsamplingError, ResetError

from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

class Measurements(DataIO):


    def __init__(self, _material: str):

        file_name = self.get_file()

        self.values = None

        if file_name:
            self.file_name = file_name
            self.values = self.read_file(file_name)
        else:
            raise ImportError("No files were imported!")

        if self.values.any() == None:
            raise ValueError("Values were not set!")

        # print(self.values)
        # print(np.shape(self.values))

        self.background_removed_reference = False
        self.background_removed_spectrum = False
        self.x_modified = False
        #self.inversed = False

        self.mat = mat(_material)
        self.set_data()


    def set_data(self):
        self.frequency = copy.copy(self.values[0])
        bool = self.frequency[0] > self.frequency[-1]
        # print(bool)
        if bool:
            self.frequency = self.frequency[::-1]
        if len(self.values) == 3:
            self.reference = copy.copy(self.values[1])
            self.spectrum =  copy.copy(self.values[2])
            if bool:
                self.reference = self.reference[::-1]
        elif len(self.values) == 2:
            self.spectrum =  copy.copy(self.values[1])
        else:
            raise ValueError("Measurement values are out of scope!")

        if bool:
            self.spectrum = copy.copy(self.spectrum[::-1])

        self.background_removed_reference = False
        self.background_removed_spectrum = False
        self.x_modified = False


    def initial_cut(self, values: np.ndarray = None, cut: list = None):

        if (self.background_removed_reference
            or self.background_removed_spectrum
            or self.x_modified):
            raise ResetError("Please reset the data first, to redo the selection of the main area!")

        # print("inside function:")
        # print(np.shape(self.values))
        # print(np.size(values))
        if not np.asarray(values).any():
            raise ValueError("x has to be array like and not all zeros!")
        if not np.asarray(cut).any():
            raise ValueError("x has to be array like and not all zeros!")
        # print("Cutting area: {}".format(cut))
        # print("Initial Array:\n{}".format(values))
        return  values[( self.frequency > cut[0]) & ( self.frequency < cut[1])]


    def inverse_value(self,value) -> np.ndarray:
        #self.inversed = True
        return value[::-1]


    def modify_X(self,
                x,
                y,
                initial_offset_x = np.array([-.75,-.6,.56,.75]),
                initial_offset_y = 0,
                initial_amps=np.array([0.2,0.1,0.3,0.4]),
                initial_widths=np.ones(4)*0.025,
                set: str = "reference",
                polyfit_degree: int=8
            ):

        if not getattr(self, "background_removed_" + set):
            raise BackgroundRemoveError("Please execute the background removal first!")

        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        initial_offset_x = np.array([find_nearest(x,initial_offset_x[i]) for i in range(4)])

        y_p0 = []
        y_p0 = np.append(y_p0,(initial_amps,initial_offset_x,initial_widths))
        y_p0 = np.append(y_p0,initial_offset_y)

        # inverse_y = 1/y - 1

        def reffit(x,*k):
            a=[k[i] for i in range(0,4)]
            b=[k[i] for i in range(4,8)]
            c=[k[i] for i in range(8,12)]
            d=k[12]
            return -((aux.gauss_func(x,a[0],b[0],c[0])-aux.lorentz_func(x,a[0]*0.8,b[0],c[0]*0.2))+ # peak 1
                    (aux.gauss_func(x,a[1],b[1],c[1])-aux.lorentz_func(x,a[1]*0.8,b[1],c[1]*0.2))+ # peak 2
                    (aux.gauss_func(x,a[2],b[2],c[2])-aux.lorentz_func(x,a[2]*0.8,b[2],c[2]*0.2))+ # peak 3
                    (aux.gauss_func(x,a[3],b[3],c[3])-aux.lorentz_func(x,a[3]*0.8,b[3],c[3]*0.2)))+d # peak 4 + offset

        # fit reffit (guass and negativ lorentz) to ref measurement
        p_ref, _ = curve_fit(reffit, x, y, p0=y_p0, maxfev=1000)
        # get position of peaks in V and f
        self.peaks = np.array([p_ref[i] for i in range(4,8)])
        # x_peaks = [find_nearest(x, self.peaks[i]) for i in range(4)]

        self.x_modified = True

        return np.polyval(np.polyfit(self.peaks,self.mat.Hf,polyfit_degree),x)


    def _remove_background(self, x, y, set: str = "spectrum") -> np.ndarray:
 
        if getattr(self, "background_removed_" + set):
            raise BackgroundRemoveError("Reset data before executing this method again!")
        
        # if np.amax(y) > 0 and np.amin(y) < 0 :
            # y += np.abs(np.amin(y)) + 0.5
        # if y[0] > y[-1]:
            # y += np.abs(np.amin(y)) + 0.5
            
        y = -(y - 2 * np.amax(y))
            
        baseline_fitter = Baseline(x_data=x)
        
        setattr(self, "inverse_" + set, y)
        setattr(self, "background_" + set, baseline_fitter.iasls(y)[0])
        
        return_y = y/getattr(self, "background_" + set)

        setattr(self, "background_removed_" + set, True)

        return -(return_y-2)

    def remove_background(self, x, y, cut1: list=[], cut2: list=[], polyfit_degree=8, set: str = "spectrum") -> np.ndarray:

        if getattr(self, "background_removed_" + set):
            raise BackgroundRemoveError("Reset data before executing this method again!")

        if np.amax(y) > 0 and np.amin(y) < 0 :
            y += np.abs(np.amin(y)) + 0.5

        x_cutted = x[(x<cut1[0]) | ((x>cut1[1]) & (x<cut2[0])) | (x>cut2[1])]
        y_cutted = y[(x<cut1[0]) | ((x>cut1[1]) & (x<cut2[0])) | (x>cut2[1])]
        
        setattr(self, "background_polyfit_" + set, np.polyval(np.polyfit(x_cutted,y_cutted,polyfit_degree), x))

        return_y = y/getattr(self, "background_polyfit_" + set)

        setattr(self, "background_removed_" + set, True)

        return return_y


    def subsampling(self, x = np.array([]), y = np.array([]), highres_range = [], sampling = 10):#, range_tol = 1e9, flim = 2.5e9):

        range_tol=1e9
        flim=2.5e9

        if not any(highres_range):
            raise ValueError("Please set a high resolution area.")
            # highres_range = [self.mat.Hf[2] - range_tol, self.mat.Hf[3] + range_tol]
        if not any(x):
            x = self.frequency[(flim<self.frequency)]
        if not any(y):
            y = self.spectrum[(flim<self.frequency)]

        if highres_range[0] < np.amin(x):
            highres_range[0]=np.min(x)
        if highres_range[0] > np.amax(x):
            highres_range[0]=np.max(x)

        x_res1=[x[(x<highres_range[0])], x[(x>highres_range[1])]]
        y_res1=[y[(x<highres_range[0])], y[(x>highres_range[1])]]

        inter=[interp1d(x_res1[i],y_res1[i]) for i in range(2)] #interpolating measurement
        x_res=[x_res1[i][::sampling] for i in range(2)]  #resampling frequency
        y_res=[inter[i](x_res[i]) for i in range(2)] #resampling measurements using the interpolation to the resampled frequency

        x_r=np.array([])
        y_r=np.array([])

        x_r=np.append(x_r,x_res[0])
        x_r=np.append(x_r,x[(x>=highres_range[0]) & (x<=highres_range[1])]) #placing EIT range in resampled data
        y_r=np.append(y_r,y_res[0])
        y_r=np.append(y_r,y[(x>=highres_range[0]) & (x<=highres_range[1])]) #placing EIT range in resampled data

        x_r=np.append(x_r,x_res[1])
        y_r=np.append(y_r,y_res[1])


        return x_r, y_r


if __name__ == "__main__":
    print("Please Import me")
