from spectralEIT.bin.constants import constants as con

import numpy as np

def cesium_number_density(T):
# C. B. Alcock, V. P. Itkin & M. K. Horrigan: Vapour Pressure Equations for the Metallic Elements: 298–2500K, Pages 309-313 | Published online: 18 Jul 2013
    if T < 301.65: # ceseium melting point
        p = 10.0**(4.711 - 3999. / T)
    else:
        p = 10.0**(8.232 - 4062. / T - 1.3359 * np.log(T))
    return 101325.0*p/(con.kB*T)

def rubidium_number_density(T):
# C. B. Alcock, V. P. Itkin & M. K. Horrigan: Vapour Pressure Equations for the Metallic Elements: 298–2500K, Pages 309-313 | Published online: 18 Jul 2013
    if T < 312.45: # rubidium melting point
        p = 10.0**(4.857 - 4215. / T)
    else:
        p = 10.0**(4.312 - 4040. / T)
    return 101325.0*p/(con.kB*T)

def sodium_number_density(T):
# C. B. Alcock, V. P. Itkin & M. K. Horrigan: Vapour Pressure Equations for the Metallic Elements: 298–2500K, Pages 309-313 | Published online: 18 Jul 2013
    if T < 370.95: # rubidium melting point
        p = 10.0**(5.298 - 5603. / T)
    else:
        p = 10.0**(4.704 - 5377. / T)
    return 101325.0*p/(con.kB*T)   

def potassium_number_density(T):
# C. B. Alcock, V. P. Itkin & M. K. Horrigan: Vapour Pressure Equations for the Metallic Elements: 298–2500K, Pages 309-313 | Published online: 18 Jul 2013
    if T < 336.8: # rubidium melting point
        p = 10.0**(7.9667 - 4646. / T)
    else:
        p = 10.0**(7.4077 - 4453. / T)
    return 101325.0*p/(con.kB*T)   
