import numpy as np

import json

import spectralEIT.bin.auxiliary_func as aux
import logging

from spectralEIT.bin.constants import constants as con
from spectralEIT.bin.parameters import Parameters as par
from spectralEIT.bin.material import Material as mat
from spectralEIT.bin.string_manipulation import format_float_to_scale

class LightPropagation():

    def __init__(self, parameters=None):

        self.logger = logging.getLogger(__name__)
        self.logger.info("Setting calculation in LightPropagation")

        if parameters == None:
            raise ValueError("No parameters were given!")

        self.set_parameters(parameters)


    def set_parameters(self, parameters):
        self.parameter_dict = parameters
        self.par = par(parameters)
        self.logger.info("Calculation parameters: %s", json.dumps(parameters, indent=2) if parameters is not None else {})


    def _init_variables(self):
        self.logger.info("Initiate variables")
        self.reset()
        self.cancelBool = False
        self.z,self.dz     = np.linspace(0,self.par.cellLength,self.par.zsteps,retstep=True)
        self.rabiFunction  = np.zeros(self.par.zsteps)
        self.TAbsFunctions = np.zeros([len(self.z),self.par.gridSize])
        self.chiFunction   = np.zeros([len(self.z),self.par.gridSize],dtype=complex)
        self.TAbs          = np.ones([self.par.gridSize])
        self.IinT          = np.array([])
        self.IoutT         = np.array([])
        self.IinW          = np.array([])
        self.IoutW         = np.array([])
        self.t             = np.array([])


    def reset(self):
        self.logger.info("Reset variables")
        if hasattr(self, "z"):
            del self.z
        if hasattr(self, "dz"):
            del self.dz
        if hasattr(self, "rabiFunction"):
            del self.rabiFunction
        if hasattr(self, "TAbsFunctions"):
            del self.TAbsFunctions
        if hasattr(self, "chiFunction"):
            del self.chiFunction
        if hasattr(self, "TAbs"):
            del self.TAbs
        if hasattr(self, "IinT"):
            del self.IinT
        if hasattr(self, "IoutT"):
            del self.IoutT
        if hasattr(self, "IinW"):
            del self.IinW
        if hasattr(self, "IoutW"):
            del self.IoutW
        if hasattr(self, "t"):
            del self.t
        if hasattr(self, "chiShape"):
            del self.chiShape


    ## Shape of the Rabi function a focused or guided strong laser beam
    def rabi_shape(self, z, w0f, wavelength):

        self.logger.info("Inside rabi_shape")

        z = z - self.par.posLC

        self.logger.info("z is: %s m, with LC position: %s m", format_float_to_scale(z), format_float_to_scale(self.par.posLC))

        if z < 0:
            return self.cell_prop(z, prop="Free Space", w0=w0f, wavelength=wavelength)
        elif 0 <= z <= self.par.lcLength:
            return self.cell_prop(z)
        elif self.par.lcLength < z:
            if self.behind_cell == False:
                self.behind_cell = True
            return self.cell_prop(z-self.par.lcLength, prop="Free Space", w0=w0f, wavelength=wavelength)
        else:
            raise ValueError("Error in Rabi function: z out of bounds")


    ##
    def cell_prop(self, z, prop="Light Cage", w0=None, wavelength=None):
        if prop == "Free Space":
            self.logger.info("Calculating the Rabi function for free space, with z=%s m", format_float_to_scale(z))
            zR = np.pi*w0**2/wavelength
            wz = w0 * np.sqrt(1+(z/zR)**2)
            return w0**2/wz**2
        elif prop == "Light Cage":
            self.logger.info("Calculating the Rabi function for light cage, with z=%s m", format_float_to_scale(z))  
            return 10**(self.par.lossdB*z/20)
        else:
            raise ValueError("Error in Rabi function: prop must be \"Free Space\" or \"Light Cage\"")


    def calculate(self, progress_callback=None):

        self.logger.info("Starting calculation")
        
        self._init_variables()
        
        if hasattr(self, "materials"): 
            if self.materials.name != self.par.material:
                self.materials = mat(self.par.material)
        else:
            self.materials = mat(self.par.material)
        
        wavelength = getattr(self.materials,self.materials.mat_list[0]).wavelength
        
        k0 = getattr(self.materials,self.materials.mat_list[0]).k0
        

        width0 = self.par.width0
        if self.par.propType == "focused":
            width0 = wavelength*self.par.focalLength/np.pi/self.par.width0
            self.par.widthFocused = width0

        self.logger.info("Get the Rabi frequency for either weak- or EIT-regime, current is: %s", self.par.type)
        ## get the rabi frequency
        if "weak" in self.par.type:
            rabi0 = 0
        elif "EIT" in self.par.type:
            self.logger.info("Initial Rabi frequency is, %s Hz", format_float_to_scale(self.par.rabiFrequency))
            rabi0 = self.par.rabiFrequency

        self.logger.info("Set the light shape, pulse or cw, current is %s", self.par.lightShape)
        ## create the light shape
        if self.par.lightShape == "pulse":

            self.logger.info("Creating a pulse")

            df = 2*np.max(self.par.f)/self.par.gridSize 
            self.logger.info("df is %s", format_float_to_scale(df))
            self.t = 1/df*np.arange(-self.par.gridSize/2,self.par.gridSize/2)/self.par.gridSize
            dt = 2*np.max(self.t)/np.size(self.t)
            self.logger.info("dt is %s", format_float_to_scale(dt))

            if self.par.type == "EITStandalone":
                pulseFreq = 0
            else:
                pulseFreq = self.par.pulseFreq

            E = aux.GaussPulse(self.t,self.par.dt/(2*np.sqrt(2*np.log(2))),pulseFreq) # get the gauss pulse in the time domain
            self.IinT = np.abs(E)**2
            E = np.fft.fftshift(np.fft.fft(E)*dt) # fourier transfer the gauss pulse into the frequency domain
            self.IinW = np.abs(E)**2#/np.max(nabs(E)**2)

        elif self.par.lightShape == "cw": # create a continous wave
            E = 1
        else:
            raise ValueError("Error in LightPropagation in selecting the light shape: variable lightShape must be \"pulse\" or \"cw\" ")

        self.logger.info("Set the propagation type, current is %s", self.par.propType)
        if self.par.propType == "focused":
            self.behind_cell = False
            change_rabi = True
            TFunction = 1
            for i,zStep in enumerate(self.z):
                self.logger.info("Current zStep is %s m", format_float_to_scale(zStep))
                if progress_callback != None:
                    progress_callback.emit(self.text(), int(100*zStep/self.par.cellLength))
                ## get the rabi frequency
                if "EIT" in self.par.type:
                    shape = self.rabi_shape(zStep, width0, wavelength)
                    self.logger.info("Shape of the Rabi function is: %s", format_float_to_scale(shape))
                    if self.behind_cell == True and change_rabi == True:
                        rabi0 = self.rabiFunction[i-1]
                        change_rabi = False
                    rabi = rabi0*shape
                    self.logger.info("rabi is now %s Hz", format_float_to_scale(rabi))
                    chi_e = self.chi_select(rabi)
                    self.rabiFunction[i] = rabi
                else:
                    raise ValueError("Error in LightPropagation: if the light is focused, the propagation type should be EIT!")
                n = np.sqrt(1 + chi_e) # get the refraction index
                self.chiFunction[i]  = chi_e
                TFunction *= np.exp(1j*k0*n*self.dz)
                self.TAbsFunctions[i] = np.abs(TFunction)
                rabi = rabi0
        elif self.par.propType == "unfocused":
            rabi = rabi0
            if "EIT" in self.par.type:
                chi_e = self.chi_select(rabi)
            else:
                chi_e = self.chi_select()
            self.chiShape = chi_e
            n = np.sqrt(1 + chi_e)
            TFunction = np.exp(1j*k0*n*self.par.cellLength)
        else:
            raise ValueError("Error in LightPropagation in focusing selection!")
        E *= TFunction
        self.TAbs = np.abs(TFunction)


        ## Delete the variables that are not needed anymore
        if hasattr(self, "behind_cell"):
            del self.behind_cell
        if hasattr(self, "change_rabi"):
            del change_rabi

        ## Get the intensities
        if self.par.lightShape == "pulse":
            self.IoutW = np.abs(E)**2/np.max(self.IinW)
            self.IinW /= np.max(self.IinW)
            self.IoutT = np.abs(np.fft.ifft(E)/dt)**2/np.max(self.IinT)
            self.IinT /= np.max(self.IinT)
        elif self.par.lightShape == "cw":
            self.IoutW = np.abs(E)**2

        self.logger.info("Calculation finished")


    def chi_select(self, rabi=0):
        
        self.logger.info("Inside chi_select")

        # print(self.materials.mat_list)
        chi = np.zeros(len(self.materials.mat_list), dtype=np.ndarray)
        
        self.logger.info("Go through every isotope of the material if available")
        for num, material in enumerate(self.materials.mat_list):
            self.logger.info("Current material: %s", material)
            self.mat = getattr(self.materials,material)
            # print(self.mat.__dict__)
            if "rubidium" in material:
                if "85" in material:
                    damping = self.par.mixing_rb/100
                elif "87" in material:
                    damping = (100-self.par.mixing_rb)/100
                else:
                    print("warning in damping selection / rubidium isotope")
            elif "potassium" in material:
                if "39" in material:
                    damping = (100 - self.par.mixing_k40 - self.par.mixing_k41)/100
                elif "40" in material:
                    damping = self.par.mixing_k40/100
                elif "41" in material:
                    damping = self.par.mixing_k41/100
                else:
                    print("warning in damping selection / potassium isotope")
            elif "cesium" in material or "sodium" in material:
                damping = 1
            else:
                print("warning in damping selection / material")
            if damping == 0:
                chi[num] = 0
            else:
                chi[num] = self._chi_select(damping, rabi)
        
        return np.sum(chi, axis=0)
            

    def _chi_select(self, damping=1, rabi=0):
        self.logger.info("Calculate chi with damping=%s and the Rabi frequency=%s Hz", format_float_to_scale(damping), format_float_to_scale(rabi))
        # Rabi frequency in circular angles
        rabiCirc = con.circ*np.abs(rabi)

        # Get the pre factors for the chi
        N = self.mat.number_density(self.par.Tk) / (2*(2*self.mat.I+1)) # number density
        preFactor = damping * N * self.mat.d02 / (con.ep0 * con.hbar) # prefactor
        self.logger.info("Prefactor is %s", format_float_to_scale(preFactor))
        self.logger.info("Number density is %s", format_float_to_scale(N))
        self.logger.info("d02 is %s", format_float_to_scale(self.mat.d02))

        #transitions = [0,1,2,3]
        ret=np.zeros(len(self.par.wDet),dtype=complex)

        self.logger.info("Select the type of the calculation, current is %s", self.par.type)
        # Sort out the requested calculation
        if self.par.type == "EITComplete":
            for n in self.mat.transitions:
                ret += self.mat.dFactor[n] * self.chi_function(
                        w0=self.mat.Hw[n],
                        EITDetune=np.abs(self.mat.Hw[self.par.transition]-self.mat.Hw[self.mat.EIT_config[self.par.transition]]) if n != self.par.transition else 0,
                        rabi=rabiCirc
                    )
            return preFactor * ret
        elif self.par.type == "EITStandalone":
            return preFactor * self.mat.dFactor[self.par.transition] * self.chi_function(rabi=rabiCirc)
        elif self.par.type == "EITTransition":
            return preFactor * (self.mat.dFactor[self.par.transition]
                * self.chi_function(w0=self.mat.Hw[self.par.transition],rabi=rabiCirc)
                + self.mat.dFactor[self.mat.EIT_config[self.par.transition]]
                * self.chi_function(w0=self.mat.Hw[self.mat.EIT_config[self.par.transition]],EITDetune=np.abs(self.mat.Hw[self.par.transition]-self.mat.Hw[self.mat.EIT_config[self.par.transition]]),rabi=rabiCirc))
        elif self.par.type == "EITPower":
            tran1 = self.par.transition
            match tran1:
                case 0:
                    tran2=1
                case 1:
                    tran2=0
                case 2:
                    tran2=3
                case 3:
                    tran2=2
            return preFactor * ( self.mat.dFactor[tran1]
                * self.chi_function(w0=self.mat.Hw[tran1],EITDetune=0,rabi=rabiCirc)
                + self.mat.dFactor[tran2]
                * self.chi_function(w0=self.mat.Hw[tran2],EITDetune=np.abs(self.mat.Hw[tran1]-self.mat.Hw[self.mat.EIT_config[tran1]]),rabi=rabiCirc)
                )
        elif self.par.type == "weakComplete":
            for n in self.mat.transitions:
                ret += self.mat.dFactor[n] * self.chi_function(w0=self.mat.Hw[n])
            return preFactor * ret
        elif self.par.type == "weakStandalone":
            return preFactor * self.mat.dFactor[self.par.transition] * self.chi_function()
        else:
            raise ValueError("Something wrong with \"type\" option: type = %s"%self.par.type)


    ## Auxiliary Chi function to calculate the form of the chi for a given field or fields
    def chi_function(self,w0=0,EITDetune=0,rabi=0):
        
        self.logger.info("Inside chi auxiliary function with, w0=%s Hz, EITDetune=%s Hz, rabi=%s Hz", format_float_to_scale(w0), format_float_to_scale(EITDetune), format_float_to_scale(rabi))

        delta = -(self.par.wDet - w0 - self.par.w0Det)
        deltaEIT = EITDetune - self.par.w0Det + self.par.EITDetuneCirc

        gridSize = len(self.par.wDet)

        gamma_sp = self.mat.natGamma if "EIT" in self.par.type else self.mat.natGamma/2

        gamma31 = gamma_sp + self.par.gamma_coll

        self.logger.info("Select line shape, current is %s", self.par.profile)
        if self.par.profile == "voigt": # Voigt profile includes the Lorentz and Gauss shapes
            # Set up the return values
            profileReal,profileImag = np.zeros((2,gridSize))

            # Set the constants for the Gauss function
            U  = (self.mat.w0+w0)/con.c0 * np.sqrt(con.kB*self.par.Tk/(self.mat.m0))
            a  = 4*U
            dv = 2*a/self.par.gaussSteps

            # Loop over all the velocities
            for v in np.arange(-a,a-dv,dv):

                # Check if the calculation is cancelled
                if self.cancelBool == True:
                    self.logger.info("Calculation cancelled")
                    self.reset()
                    raise InterruptedError("Calculation cancelled")

                # calculation of the gauss and lorentz profile
                gauss = (2*np.pi*U**2)**-0.5 * np.exp(-0.5*(v**2)/(U**2))
                if "EIT" in self.par.type:
                    lorentzReal,lorentzImag = aux.lorentz_profile_strong(delta+v,deltaEIT+v,rabi,gamma31,self.par.gammadCirc)
                elif "weak" in self.par.type:
                    lorentzReal,lorentzImag = aux.lorentz_profile_weak(delta+v,gamma31)
                else:
                    raise ValueError("Something went wrong with the Lorentz profile: profile: %s, tyep: %s"%(self.par.profile,self.par.type))

                # numerical integral
                profileReal += lorentzReal * gauss * dv
                profileImag += lorentzImag * gauss * dv
            return profileReal + 1j * profileImag
        elif self.par.profile == "lorentz": # Only includes the Lorentz profile
            if "EIT" in self.par.type:
                profileReal,profileImag = aux.lorentz_profile_strong(delta,deltaEIT,rabi,gamma31,self.par.gammadCirc)
            elif "weak" in self.par.type:
                profileReal,profileImag = aux.lorentz_profile_weak(delta,gamma31)
            else:
                raise ValueError("Something went wrong with the Lorentz profile: profile: %s, tyep: %s"%(self.par.profile,self.par.type))
            return profileReal + 1j * profileImag
        else:
            raise ValueError("Something went wrong in the profile selection: profile: %s"%self.par.profile)
