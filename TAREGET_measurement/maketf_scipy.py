import numpy as np
import scipy.io
import scipy.interpolate
from tqdm import tqdm
import datetime
import ROOT

import target_driver
import target_io

Nsamples = 14 * 32 #capacitors (cells) to use
dac_counts = 4095 #number of input files to use
step = 8 #DAC step
sample0 = 0 #the first capacitor to use

def maketf(channel, cell):
    tf = np.zeros(int(dac_counts / step)) # prepare an array for TF
    
    for i in tqdm(range(int(dac_counts/step)), desc = "DAC counts / step", leave = False):
        counts = i * step   #current DAC value
        vped = 19.2 + 0.6 * counts #pedestal voltage
        filename = '/Volumes/Untitled/kuroda/2020target/run/20200221run/TF_acq_%d.fits' % counts #input file name

        reader = target_io.EventFileReader(filename)
        NEvents  = reader.GetNEvents()

        ampl = np.zeros([NEvents, Nsamples]) #array for ADC values in cells (waveform)

        for ievt in range(NEvents):
            rawdata = reader.GetEventPacket(ievt, channel)
            packet = target_driver.DataPacket()
            packet.Assign(rawdata, reader.GetPacketSize())

            wf = packet.GetWaveform(0)
            ampl[ievt] = wf.GetADC(sample0 + cell) #fill the array with ADC and make a waveform
        ampl[ampl == 0] = np.nan #convert zeros to NaN
        sigma = np.nanstd(ampl[:, cell]) #calculate noise std in every cell (capacitor)
        if sigma > 2.:
            tf[i] = np.nanmean(ampl[int(round(NEvents * 0.2)) : int(round(NEvents * 0.8)), cell]) #check for consistency
            sigma = np.nanstd(ampl[int(round(NEvents * 0.2)) : int(round(NEvents * 0.8)), cell])
            if sigma > 10.:
                print("std dev is still large: %f for counts: %d and voltage %f"%(sigma, counts, 19.2 + 0.6 * counts))
        else:
            tf[i] = np.nanmean(ampl[:, cell])

    return tf

for j in tqdm(range(0,64), desc = "channel"):
    tfs = [] #list of TFs for every capacitor in the channel
    x = np.arange(0, dac_counts, step).astype(float) #array for x values of the TF (voltage)
    for i in range(int(dac_counts/step)):
        x[i] = 19.2 + 0.6 * x[i]

    for i in tqdm(range(Nsamples), desc = "cells", leave = False):
        tf = maketf(j, i)
        gra = ROOT.TGraph(int(dac_counts / step), tf, x) #make a TGraph

        y = np.zeros(4096).astype(float) #array for y values of the TF (ADC)
        for i in range(350, 3500):
            y[i] = gra.Eval(float(i)) #extract values from the TGraph
        tfs.append(y) #add the TF to the list
        del tf

    scipy.io.savemat("/Volumes/Untitled/kuroda/2020target/transfer_fun/TF/20200223mat/tf_chan%i.mat" % j, {'TFs':tfs}) #save the TFs for the channel
    dt_now = datetime.datetime.now()
    print(dt_now)

