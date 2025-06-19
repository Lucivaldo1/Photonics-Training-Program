import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c

'''
@author: Lucivaldo Aguiar 
References:
https://optics.ansys.com/hc/en-us/articles/360042819293-Coupled-ring-resonator-filters
Integrated ring resonator, Dominik G. Rabus
Synthesis of a parallel-coupled ring-resonator filter, Andrea Melloni
'''
def FSR2graph (FSR):
    #this graphic is valid only and if only m1 - m2 = 1
    nm = 1e-9
    um = 1e-6
    FSR1 = np.linspace(0.1*nm,15*nm, 100)
    FSR2 = FSR/(np.abs(1-(FSR/FSR1)))
    plt.plot(FSR1/nm,FSR2/nm)
    plt.ylim(min(FSR1/nm), max(FSR2/nm))
    plt.xlim(min(FSR1/nm), max(FSR1/nm))
    plt.xlabel('FSR1 [nm]')
    plt.ylabel('FSR2 [nm]')
    plt.title(rf'$FSR_2$($FSR ={FSR/nm}, FSR_1$)')
    plt.grid()
    plt.show()
    
def ringData(x, N,ng, FSR):
    """
       Computes key parameters for a ring resonator based on input parameters.

       Inputs:
           x   : Relation FSR/B (Free Spectral Range to Bandwidth ratio)
           N   : Number of rings
           ng  : Group index of the waveguide
           FSR : Free Spectral Range

       Output:
           A dictionary containing calculated values for FSR, K, Q, g, B, and L.
       """
    dictionary ={
        'FSR' : [],
        'K' : [],
        'Q' : [],
        'g' : [],
        'B' : [],
        'L' : []
        }
    #determining FSRs and ring total length
    if N > 1:
        m1 = 3
        m2 = 2
        FSR1 = FSR/m1
        FSR2 = (m1/m2)*FSR1
        dictionary['FSR'].extend([FSR1,FSR2])
        #ring total length
        l1 = (1550e-9**2)/(ng*FSR1)
        l2 = (1550e-9**2)/(ng*FSR2)
        dictionary['L'].extend([l1,l2])
    else:
        dictionary['FSR'].append(FSR)
        l = (1550e-9**2)/(ng*FSR)
        dictionary['L'].append(l)
        
    for n in range(1,3):
        #Computing parameters based on Melloni's method
        g = np.sqrt(2) * np.sin((2*n-1)/(2*N) * np.pi)
        B = FSR / x
        Q = FSR/(B*g)
        K = ((np.pi**2)/(2*Q**2))*(np.sqrt(1 + (4*Q**2)/(np.pi**2)-1))

        dictionary['g'].append(g)
        dictionary['Q'].append(FSR/(B*g))    
        dictionary['K'].append(K)
        dictionary['B'].append(B)
    #Computing coupling coefficient for the middle ring
    dictionary['K'].append(np.sqrt(0.25)*(dictionary['K'][0])**2)
    return dictionary

def placeOna(icApi,name,x,y, inputs, nmbrofpoints, startFrequency, stopFrequency):
    '''
    places an Ona at x,y coordinates
    :param name:
    :param inputs:
    :param nmbrofpoints:
    :return:
    '''
    icApi.swichtolayout()
    icApi.addelement('Optical Network Analyzer')
    icApi.set('name', name)
    icApi.setposition(name, x, y)
    icApi.set('number of input ports', inputs)
    icApi.set('input parameter', 2)
    icApi.set('start frequency',startFrequency)
    icApi.set('stop frequency', stopFrequency)
    icApi.set('number of points', nmbrofpoints)

    return 0

def getDeltaL(FSR, wavelength_center, ng):
    '''
    returns Delta L from ng and wavelength center
    :param FSR: float
    :param wavelength_center: float
    :param ng: float
    :return:
    '''
    L = wavelength_center**2 / (FSR * ng)

    return L

def getLpi(wavelength_center, neff):
    '''
    returns Lpi from neff and wavelength center
    :param FSR: float
    :param wavelength_center: float
    :param ng: float
    :return:
    '''
    Lpi = (wavelength_center) / (2*neff)

    return Lpi

def MZILatticefilter(icApi, ordem, neff, ng, L, deltaL,k):
    icApi.switchtolayout()
    for i in range(0,5,1):
        icApi.addelement('Waveguide Coupler')
        icApi.set('name',f'dc{i+1}')
        icApi.setposition(f'dc{i+1}', 400+(400*i), 100)
        icApi.set('coupling coefficient 1', k[i])
    for i in range(0,8,1):
        icApi.addelement('Straight Waveguide')
        icApi.set('name',f'wg{i+1}')
        icApi.set('effective index 1', neff)
        icApi.set('group index 1', ng)
        icApi.set('length', L if i%2!=0 else deltaL[i])
        icApi.setposition(f'wg{i+1}', 550+(400 * (i if i%2!=0 else i-1)), 60 if i%2!=0 else 160)
    return 0