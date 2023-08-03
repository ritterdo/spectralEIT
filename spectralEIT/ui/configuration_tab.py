import sys
import os

from PyQt5.QtWidgets import QWidget, QMessageBox, QProgressBar
from PyQt5 import uic

from scipy.optimize import curve_fit

import numpy as np

import spectralEIT.bin.info_windows as info
import spectralEIT.bin.string_manipulation as stringManipu
import spectralEIT.bin.workers as workers
import spectralEIT.bin.calculation as calc

from spectralEIT.bin.default_parameters import DEFAULT_PARAMETER_DICT
from spectralEIT.bin.fit_parameters import fit_params_bound, fit_params_list
from spectralEIT.bin.exceptions import ThreadError
from spectralEIT.bin.default_config import DefaultClass, NUMBER_TYPES, PAR_DICT_INT_TYPE

class ConfigurationTab(QWidget, DefaultClass):



    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        DefaultClass.__init__(self, __name__)

        self.logger.info("Initiate ConfigurationTab")

        self.load_ui("configurationTab.ui")
        
        self.lastPressedButton = "None"

        self.pushButton_default_parameters.clicked.connect(lambda: self.load_parameters(every="all"))
        self.pushButton_startCalculation.clicked.connect(self.start_calculation)
        self.pushButton_saveParameters.clicked.connect(self.save_parameters)
        self.pushButton_startFit.clicked.connect(self.start_fitting)
        self.pushButton_cancel.clicked.connect(self.cancel_calculation)
        # try:
        #     self.checkBox_use_measurement_frequency.clicked.connect(self.use_measurement_frequency)
        # except Exception:
        #     info.showCriticalErrorBox(sys.exc_info())

        ## Connect parameter comboBoxes to corresponding functions for error free parameter input
        self.comboBox_lightShape.activated.connect(self.light_shape_option)
        self.comboBox_prop.activated.connect(self.prop_option)
        self.comboBox_propType.activated.connect(self.prop_type_option)
        self.comboBox_type.activated.connect(self.type_option)
        self.comboBox_profile.activated.connect(self.profile_option)
        self.comboBox_material.activated.connect(self.material_option)

        self.setup_tool_tips()
        self.import_material()
        self.load_parameters(every="all")
        # self.set_default_values()

        self.refresh_ui()


    def setup_tool_tips(self):
        self.label_par_rabiFrequency.setToolTip("Maximal Rabi frequency in the setup [Hz]")
        self.label_par_width0.setToolTip("Width of the Gauss Beam [m]")
        self.label_par_cellLength.setToolTip("Length of the Cesium Cell [m]")
        self.label_par_focalLength.setToolTip("Focal Length of the Lense in front of the Cell")
        self.label_par_lcLength.setToolTip("Length of the Light Cage inside the Cesium Cell [m]")
        self.label_par_posLC.setToolTip("Distance of the front of the Cesium Cell and the front of the Light Cage [m]")
        self.label_par_lightShape.setToolTip("Shape of the incoming light:\tcw\t- continuous Wave\n\t\t\t\tpulse\t- pulsed Light")
        self.label_par_prop.setToolTip("prop:\tFree Space\t- Free space propagation of the light for the focused light beam\n\tLight Cage\t- Propgation through a light cage")
        self.label_par_propType.setToolTip("Focused:\tunfocused\t- Light is collimated\n\tfocused\t\t- Light is focused on the light cage beginning either with or without a light cage")
        self.label_par_dt.setToolTip("Duration of the Light Pulse [s]")
        self.label_par_pulseFreq.setToolTip("Number of the Pulse Frequency in respect of the Transitions if the Light Pulse differs from the desired Transition")
        self.label_par_T.setToolTip("Temperature of the Cesium Cell [˚C]")
        self.label_par_zsteps.setToolTip("Number of Segments of the Light Cage for the Propagation Caluclation")
        self.label_par_profile.setToolTip("Chi Profile:\tlorentz\t- Lorentz profile as chi shape in frequency space\n\t\tvoigt\t- Voigt profile as chi shape in frequency space, includes Doppler broadening of the lorentz profile")
        self.label_par_transition.setToolTip("Transition Number for EIT, starting from 0, 1, 2, 3 for the transitions")
        self.label_par_type.setToolTip("Type:\tEITComplete\t- Complete spectrum with one EIT transistion\n\tEITStandalone\t- Only one transistion with the EIT\n\tEITTransition\t- Two transistion for the probe beam with EIT and the coupling beam\n\tEITPower\t- Only the two transitions which does not flatten out due too power broadening of the coupling laser\n\tweakComplete\t- Complete spectrum without EIT\n\tweakStandalone\t- One transistion without EIT")
        self.label_par_gaussSteps.setToolTip("Number of Steps in the Doppler Broadening Calculation")
        self.label_par_EITDetune.setToolTip("Coupling Laser Detune [Hz]")
        self.label_par_f0det.setToolTip("Probe Laser Detune [Hz]")
        self.label_par_gammad.setToolTip("Ground-State Decoherence Rate [Hz]")
        self.label_par_gamma_coll.setToolTip("Collision Broadening Rate [Hz]")
        self.label_par_lossdB.setToolTip("Losses inside the light cage [dB]")
        self.label_par_mixing_rb.setToolTip("Rubidium 95 amoung in mol fraction [%]")
        self.label_par_mixing_k40.setToolTip("Potassium 40 amoung in mol fraction [%]")
        self.label_par_mixing_k41.setToolTip("Potassium 41 amoung in mol fraction [%]")


    def light_shape_option(self):
        if self.comboBox_lightShape.currentText() == "cw":
            self.textEdit_par_dt.setEnabled(False)
            self.textEdit_par_pulseFreq.setEnabled(False)
        elif self.comboBox_lightShape.currentText() == "pulse":
            self.textEdit_par_dt.setEnabled(True)
            self.textEdit_par_pulseFreq.setEnabled(True)
            self.type_option()
        else:
            info.showInfoBox("No light shape was set!")


    def prop_option(self):
        if self.comboBox_prop.currentText() == "Light Cage":
            self.comboBox_propType.setEnabled(False)
            self.comboBox_propType.setCurrentText("focused")
            self.textEdit_par_lcLength.setEnabled(True)
            self.textEdit_par_posLC.setEnabled(True)
            self.textEdit_par_lossdB.setEnabled(True)
            self.textEdit_par_zsteps.setEnabled(True)
        elif self.comboBox_prop.currentText() == "Free Space":
            self.comboBox_propType.setEnabled(True)
            self.textEdit_par_lcLength.setEnabled(False)
            self.textEdit_par_posLC.setEnabled(False)
            self.textEdit_par_lossdB.setEnabled(False)
            self.textEdit_par_zsteps.setEnabled(False)
        else:
            info.showInfoBox("No propagation type was set!")
        self.prop_type_option()


    def prop_type_option(self):
        if self.comboBox_propType.currentText() == "focused":
            self.textEdit_par_focalLength.setEnabled(True)
            self.textEdit_par_zsteps.setEnabled(True)
        elif self.comboBox_propType.currentText() == "unfocused":
            self.textEdit_par_focalLength.setEnabled(False)
            self.textEdit_par_zsteps.setEnabled(False)
        else:
            info.showInfoBox("Is the light focused was not set!")


    def type_option(self):
        if "EIT" in self.comboBox_type.currentText():
            self.textEdit_par_rabiFrequency.setEnabled(True)
            self.textEdit_par_EITDetune.setEnabled(True)
            self.textEdit_par_transition.setEnabled(True)
            if self.comboBox_type.currentText() == "EITStandalone":
                self.textEdit_par_pulseFreq.setEnabled(False)
            elif self.comboBox_lightShape.currentText() == "pulse":
                self.textEdit_par_pulseFreq.setEnabled(True)
        elif "weak" in self.comboBox_type.currentText():
            self.textEdit_par_rabiFrequency.setEnabled(False)
            self.textEdit_par_EITDetune.setEnabled(False)
            self.textEdit_par_transition.setEnabled(False)
        else:
            info.showInfoBox("No calculation type was set!")


    def profile_option(self):
        if self.comboBox_profile.currentText() == "voigt":
            self.textEdit_par_gaussSteps.setEnabled(True)
        elif self.comboBox_profile.currentText() == "lorentz":
            self.textEdit_par_gaussSteps.setEnabled(False)
        else:
            info.showInfoBox("No shape profile was set!")


    def material_option(self):
        if "cesium" in self.comboBox_material.currentText():
            
            self.label_par_mixing_rb.hide()
            self.textEdit_par_mixing_rb.hide()
            self.checkBox_mixing_rb.hide()
            
            self.label_par_mixing_k40.hide()
            self.textEdit_par_mixing_k40.hide()
            self.checkBox_mixing_k40.hide()
            
            
            self.label_par_mixing_k41.hide()
            self.textEdit_par_mixing_k41.hide()
            self.checkBox_mixing_k41.hide()
            
        elif "rubidium" in self.comboBox_material.currentText():
            
            self.label_par_mixing_rb.show()
            self.textEdit_par_mixing_rb.show()
            self.checkBox_mixing_rb.show()
            
            self.label_par_mixing_k40.hide()
            self.textEdit_par_mixing_k40.hide()
            self.checkBox_mixing_k40.hide()
            
            
            self.label_par_mixing_k41.hide()
            self.textEdit_par_mixing_k41.hide()
            self.checkBox_mixing_k41.hide()
            
        elif "potassium" in self.comboBox_material.currentText():
            
            self.label_par_mixing_rb.hide()
            self.textEdit_par_mixing_rb.hide()
            self.checkBox_mixing_rb.hide()
            
            self.label_par_mixing_k40.show()
            self.textEdit_par_mixing_k40.show()
            self.checkBox_mixing_k40.show()
            
            
            self.label_par_mixing_k41.show()
            self.textEdit_par_mixing_k41.show()
            self.checkBox_mixing_k41.show()
        
        elif "sodium"  in self.comboBox_material.currentText():
            
            self.label_par_mixing_rb.hide()
            self.textEdit_par_mixing_rb.hide()
            self.checkBox_mixing_rb.hide()
            
            self.label_par_mixing_k40.hide()
            self.textEdit_par_mixing_k40.hide()
            self.checkBox_mixing_k40.hide()
            
            
            self.label_par_mixing_k41.hide()
            self.textEdit_par_mixing_k41.hide()
            self.checkBox_mixing_k41.hide()
            


    def refresh_ui(self):
        self.light_shape_option()
        self.prop_option()
        self.prop_type_option()
        self.type_option()
        self.material_option()


    ## get all or a subset of parameters out of the gui
    def get_parameters(self, par_list: list=[], par_dict: dict={}):
        if par_dict:
            par_list = par_dict.keys()
        return_dict = {}
        if par_list:
            for par in DEFAULT_PARAMETER_DICT.keys():
                if par in par_list:
                    if type(DEFAULT_PARAMETER_DICT[par]) in NUMBER_TYPES:
                        text = getattr(self, "textEdit_par_" + par).toPlainText()
                        if DEFAULT_PARAMETER_DICT[par] in PAR_DICT_INT_TYPE:
                            return_dict[par] = int(0 if not text else float(text))
                        else:
                            return_dict[par] = float(0 if not text else text)
                    elif type(DEFAULT_PARAMETER_DICT[par]) == str:
                        return_dict[par] = getattr(self, "comboBox_" + par).currentText()
                    else:
                        raise ValueError
            return return_dict
        else:
            for par in DEFAULT_PARAMETER_DICT.keys():
                if type(DEFAULT_PARAMETER_DICT[par]) in NUMBER_TYPES:
                    text = getattr(self, "textEdit_par_" + par).toPlainText()
                    if par in PAR_DICT_INT_TYPE:
                        return_dict[par] = int(0 if not text else float(text))
                    else:
                        return_dict[par] = float(0 if not text else text)
                elif type(DEFAULT_PARAMETER_DICT[par]) == str:
                    return_dict[par] = getattr(self, "comboBox_" + par).currentText()
                else:
                    raise ValueError
            return return_dict


    ## load given parameters or the default parametersinto the gui
    def load_parameters(self, every: str=None, par_dict: dict={}):
        # print(par_dict)
        par_list=[]
        if every:
            every = every.lower()
        elif par_dict:
            par_list = par_dict.keys()
        else:
            info.showCriticalMessageBox("Something went wrong in load_parameters!")
            return None
        try:
            for key in DEFAULT_PARAMETER_DICT.keys():
                if key in par_list:
                    value = par_dict[key]
                else:
                    value = DEFAULT_PARAMETER_DICT[key]
                if type(value) == str:
                    getattr(self, "comboBox_"+key).setCurrentText(stringManipu.format_float_to_scale(value))
                elif type(value) in NUMBER_TYPES :
                    getattr(self, "textEdit_par_"+key).setText(stringManipu.format_float_to_scale(value))
                else:
                    raise ValueError
            self.refresh_ui()
        except Exception:
            info.showCriticalErrorBox(sys.exc_info())
            return None


    def check_check_boxes(self):
        return_list = []

        for par in fit_params_list:
            attr = getattr(self, "checkBox_" + par)
            if attr.isChecked():
                return_list.append(par)
                attr.setChecked(False)

        return return_list


    def save_parameters(self):
        self.window().calc_list.currentItem().set_parameters(self.get_parameters())


    def cancel_calculation(self):
        current = self.window().calc_list.currentItem()
        if current.text() in self.window().threadIsRunning.keys():
            current.cancelBool = True


    def close_calculation(self, name=None, type=None):#
        if not name:
            name = self.window().calc_list.currentItem().text()
        if name in self.window().threadIsRunning.keys():
            try:
                self.window().statusbar.removeWidget(getattr(self, "progressBar_{}".format(name)))
                delattr(self, "progressBar_{}".format(name))
                self.logger.info("%s: Progressbar deleted for %s", type, name)
            except:
                self.logger.info("%s: Progressbar not found for %s", type, name)
            self.window().threadIsRunning.pop(name)
            self.logger.info("%s: Thread deleted: %s", type, name)
            self.logger.info("%s: Total threads: %s", type, self.window().threadIsRunning)
        


    ############################
    ##                        ##
    ##      Calculation       ##
    ##                        ##
    ############################
    def start_calculation(self):
        self.logger.info("Starting Calculation")
        self.lastPressedButton="CALCULATION"
        if self.window().calc_list.count() == 0:
            self.window().calc_list.add_item(
                    _parent = self.window().calc_list,
                    parameters = self.get_parameters(),
                    item_name = "calc"
                )
        name = self.window().calc_list.currentItem().text()
        self.logger.info("CALCULATION: Calculation name: %s", name)
        try:
            if name in self.window().threadIsRunning.keys():
                raise ThreadError("CALCULATION: Calculation already running")
        except Exception as e:
            info.showCriticalErrorBox(sys.exc_info())
            return

        try:
            self.window().threadIsRunning[name] = True
            self.logger.info("ThreadIsRunning: %s", self.window().threadIsRunning)
            self.window().statusbarMessage.setText("Calculating...")

            setattr(self, "progressBar_{}".format(name), QProgressBar(self.window()))
            tmp = getattr(self, "progressBar_{}".format(name), None)
            tmp.setFormat("{name} - %p%".format(name=name))
            self.window().statusbar.addWidget(tmp)
            self.logger.info("CALCULATION: Progressbar %s created", name)   
        except Exception as e:
            self.calculation_error_function(sys.exc_info(),name)
            return           

        try:
            self.logger.info("CALCULATION: Setting up working thread")
            worker = workers.Worker(self.calculation_function, objectName = name)
            worker.signals.result.connect(self.calculation_result_function)
            worker.signals.finished.connect(self.calculation_finished_function)
            worker.signals.progress.connect(self.calculation_progress_function)
            worker.signals.error.connect(self.calculation_error_function)
            worker.signals.cancelled.connect(lambda: self.close_calculation(type="CALCULATION"))
        except Exception as e:
            self.calculation_error_function(sys.exc_info(),name)
            return

        self.logger.info("CALCULATION: Starting worker %s", name)
        self.window().threadpool.start(worker)


    def calculation_function(self, progress_callback, objectName):
        self.save_parameters()

        self.window().calc_list.currentItem().calculate(progress_callback)
        return


    def calculation_result_function(self, name):
        item = self.window().calc_list.get_item(name)
        self.window().calc_list.itemChanged.emit(item)

        self.window().statusbar.removeWidget(getattr(self, "progressBar_{}".format(name)))
        delattr(self, "progressBar_{}".format(name))
        self.logger.info("CALCULATION: Progressbar %s deleted", name)

        self.window().threadIsRunning.pop(name)
        self.logger.info("CALCULATION: Thread deleted: %s", name)
        self.logger.info("CALCULATION: Total threads: %s", self.window().threadIsRunning)
        info.showInfoBox("CALCULATION: Finished of parameter set {}!".format(name))


    def calculation_finished_function(self):
        if not any(self.window().threadIsRunning):
            self.window().statusbarMessage.setText("Ready")
        else:
            self.window().statusbarMessage.setText("Calculating...")


    def calculation_progress_function(self, name, progress):
        self.logger.info("CALCULATION: Progressbar %s set to %s", name, progress)
        progressBar = getattr(self, "progressBar_{}".format(name), None)
        progressBar.setValue(progress)


    def calculation_error_function(self, exception, name):
        info.showCriticalErrorBox(exception)
        self.close_calculation(type="CALCULATION", name=name)


    ############################
    ##                        ##
    ##        Fitting         ##
    ##                        ##
    ############################
    def start_fitting(self):

        self.logger.info("Start fitting")

        self.lastPressedButton="FITTING"

        try:
            calc_name = self.window().calc_list.currentItem().text()
            self.logger.info("FITTING: Calculation name: %s", calc_name)
            plotable_item = self.window().plotable_list.currentItem()
            measurement = getattr(plotable_item.parent_item, plotable_item.text())
            self.logger.info("FITTING: Measurement: %s", plotable_item.text())

            freq, _ = measurement.getData()

            self.textEdit_par_freqStart.setText(str(np.min(freq)))
            self.textEdit_par_freqStop.setText(str(np.max(freq)))
            self.textEdit_par_freqSteps.setText(str(len(freq)))
        except AttributeError as e:
            info.showCriticalMessageBox("FITTING: Error: Did you select a measurement to fit?\n\nThe measurement must be the current selected item in the 'Plotable Item List'.")
            return
        except Exception as e:
            info.showCriticalErrorBox(sys.exc_info())
            return

        self.logger.info("FITTING: Fitting of measurement %s with the calculation %s", plotable_item.text(), calc_name)

        try:
            if calc_name in self.window().threadIsRunning.keys():
                raise ThreadError("FITTING: Calculation already running")
        except Exception as e:
            info.showCriticalErrorBox(sys.exc_info())
            return

        try:
            self.logger.info("FITTING: Setting up working thread")
            worker = workers.Worker(self.fitting_start, measurement, objectName=calc_name)
            worker.signals.result.connect(self.fitting_result)
            worker.signals.finished.connect(self.fitting_finished)
            worker.signals.progress.connect(self.fitting_progress)
            worker.signals.error.connect(self.fitting_error)
            worker.signals.cancelled.connect(lambda: self.close_calculation(type="FITTING"))
        except Exception as e:
            self.fitting_error(sys.exec_info(), calc_name)
            return

        self.logger.info("FITTING: Starting worker %s", calc_name)
        try:
            self.window().threadpool.start(worker)
        except Exception as e:
            self.fitting_error(e, calc_name)
            return


    def fitting_start(self, measurement, objectName, progress_callback):

        sim = self.window().calc_list.get_item(objectName)
        x_data, y_data = measurement.getData()
        checkedParams = self.check_check_boxes()
        
        if checkedParams:
            param = self.get_parameters(par_list=checkedParams)
        else:
            raise ValueError("FITTING: checkedParams in fitting function where not set! Please check the fit parameters.")

        self.window().threadIsRunning[objectName] = True
        self.window().statusbarMessage.setText("Calculating...")

        fitParams, fitCov = curve_fit(
                lambda x, *fitpara: self.fitting_function_IoutW(x, {k:v for k,v in zip(param.keys(),fitpara)}),
                x_data,
                y_data,
                p0=[param[k] for k in param.keys()],
                bounds=([fit_params_bound[k][0] for k in param.keys()] ,[fit_params_bound[k][1] for k in param.keys()])
            )
        fitParams = {k:v for k,v in zip(param.keys(), fitParams)}

        parameter_dict = self.get_parameters()

        for keys in fitParams.keys():
            parameter_dict[keys] = fitParams[keys]
        
        sim.set_parameters(parameter_dict)
        sim.calculate()
        sim.fitCov = {k:v for k,v in zip(param.keys(), fitCov)}
        return


    def fitting_function_IoutW(self, freq, par_dict):
        parameter_dictionary = self.get_parameters()
        for keys in par_dict.keys():
            parameter_dictionary[keys] = par_dict[keys]

        csCalc = calc.LightPropagation(parameter_dictionary)
        csCalc.calculate()
        return csCalc.IoutW


    def fitting_result(self, name):
        item = self.window().calc_list.get_item(name)
        self.window().calc_list.itemChanged.emit(item)
        self.load_parameters(par_dict=item.parameter_dict)
        self.window().threadIsRunning.pop(name)
        info.showInfoBox("FITTING: Calculation finished of parameter set {}!".format(name))


    def fitting_finished(self):
        if not any(self.window().threadIsRunning):
            self.window().statusbarMessage.setText("Ready")
        else:
            self.window().statusbarMessage.setText("Calculating...")


    def fitting_progress(self):
        return


    def fitting_error(self, exception, name):
        info.showCriticalErrorBox(exception)
        self.close_calculation(type="FITTING", name=name)
