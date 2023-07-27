from PyQt5.QtWidgets import QFileDialog
import numpy as np
import pandas as pd
from os import getcwd

class DataIO():

    def read_file(self, file_name, skiprow_number=1, skiprow_bool=True):
        if file_name.endswith(".txt"):
            if skiprow_bool == True:
                # Get the data and replace the , with .
                inputArray = np.array([[s.replace(",",".") for s in array] for array in np.loadtxt(file_name, dtype=np.str_, skiprows=skiprow_number)])
            else:
                inputArray = np.array([[s.replace(",",".") for s in array] for array in np.loadtxt(file_name, dtype=np.str_)])
            # print(inputArray)
            if len(inputArray[0]) == 2:
                return np.array([np.float32(inputArray[:,0]), np.float32(inputArray[:,1])])
            elif len(inputArray[0]) == 4:
                return np.array([np.float32(inputArray[:,0]), np.float32(inputArray[:,1]), np.float32(inputArray[:,3])])
            elif len(inputArray[0]) == 6:
                return np.array([np.float32(inputArray[:,0]), np.float32(inputArray[:,1]), np.float32(inputArray[:,5])])
            else:
                raise ValueError("Something went wrong in read_file: length of inputArray = %d"%len(inputArray[0]))
        elif file_name.endswith(".csv"):
            skiprow_number = 0
            data = pd.read_csv(file_name, header=skiprow_number, delimiter=",")
            if " IN2" not in data.keys():
                return np.array([data["TIME ms"].to_numpy(),data[" IN1"].to_numpy()])
            elif " IN2" in data.keys():
                return np.array([data["TIME ms"].to_numpy(),data[" IN1"].to_numpy(),data[" IN2"].to_numpy()])
            else:
                raise ValueError("Something went wrong in read_file")
        else:
            raise ImportError("Unsupported file type.")

    def get_file(self, dir: str=getcwd()):
        fileName,_ = QFileDialog.getOpenFileName(None, caption="Import Measurement", directory=dir)
        if fileName:
            return fileName
        else:
            return None
