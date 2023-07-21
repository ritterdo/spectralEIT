import numpy as np

## Gauss pulse function
def GaussPulse(t,dt,f,t0=0):
    return np.exp(-(t-t0)**2/(2*dt**2))*np.exp(1j*2*np.pi*f*t)/np.sqrt(2*np.pi*dt)

def LinFunc(x,a,b):
    return a*x+b

def QuadFunc(x,a,b,c):
    return a*x**2+b*x+c

def QuartFunc(x,a,b,c,d,e):
    return a*x**4+b*x**3+c*x**2+d*x+e

def gauss_func(x,a,b,c):
    return a*np.exp(-(x-b)**2/(2*c**2))

def lorentz_func(x,a,b,c):
    lorn=(1/(np.pi))*((0.5*c)/((x-b)**2+(0.5*c)**2))
    return a*lorn/np.max(lorn)

## Fleischhauer
def lorentz_profile_strong(delta1,delta2,rabi,gamma,gammad):
    delta = delta1 - delta2
    div = np.abs(rabi**2+(gamma+2j*delta1)*(gammad+2j*delta))**2
    lorentzReal = 4*delta*(rabi**2-4*delta*delta1)-4*delta1*gammad**2
    lorentzImag = 8*delta**2*gamma+2*gammad*(rabi**2+gamma*gammad)
    return lorentzReal/div,lorentzImag/div

## Kowalski
def lorentz_profile_strong_kowalski(delta1,delta2,rabi,gamma, gammad):
    chi = 1j/(gamma-1j*delta1+rabi**2/(gammad-1j*(delta1-delta2)))
    return chi.real,chi.imag

### two level lorentzian with power broadening
def lorentz_profile_power(delta,gamma,rabi, natGamma):
    profile = (natGamma/2)*(-delta+1j*gamma) / (gamma**2 + delta**2 + (gamma/natGamma)*rabi**2)
    return profile.real, profile.imag

## two level lorentzian in a weak field
def lorentz_profile_weak(delta,gamma):
    #profile = 1j / (gamma - 1j*delta)
    profile = -1 / (delta + 1j*gamma)
    return profile.real, profile.imag
