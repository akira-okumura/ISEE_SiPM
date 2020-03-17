import numpy as np
import math
import ROOT
import sys
import os

import isee_sipm

s = 1 # (s)
ms = 1e-3 * s # (ms)
us = 1e-6 * s # (us)
ns = 1e-9 * s # (ns)

V = 1 # (V)
mV = 1e-3 * V # (mV)

class PMT:
    def __init__(self, angle, channel, name = 'hists', integ_off = 355, width = 30):
        self.name = name
        #self.mean = 0
        self.angle = angle
        self.channel = channel
        self.meanerror = 0
        
        self.hist = ROOT.TH1D()
        self.nhist = ROOT.TH1D()

        self.Ppeak = 0 #Pedestal mean
        self.Opeak = 0 #1 PE mean
        self.Ppeak_err = 0
        self.Opeak_err = 0

        self.nominal_period = 500 * ns # LED period
        self.integ_off = 433 * ns # LED location # change
        self.noise_integ_off = self.integ_off - 100 * ns # noise location # change
        self.integ_window = 30 * ns  # peak width #change




    def Create_hist(self):
        self.Cal_Hist()
        self.Save_Hist()

    def Cal_Hist(self):
        self.gz_file = 'ch%d_%s.txt.gz' % (self.channel, self.angle)
        
        waveforms = isee_sipm.gzip2waveforms(self.gz_file)
        N_pt = waveforms[0].get_n() # sampling points per waveform

        dV = waveforms[0].get_dv() # quantized delta V in (V)
        print(dV)
        dT = waveforms[0].get_dt() # sampling period 0.5 ns for 2 GHz sampling
        print(dT)

        eps = 0.001 * ns
        N_Event = int(float(N_pt) * dT / self.nominal_period) #events
        N_pt_event = int(self.nominal_period / dT) # points in a event

        integ_off_pt = int((self.integ_off + eps) / dT)
        print(integ_off_pt)
        noise_integ_off_pt = int((self.noise_integ_off + eps) / dT)
        print(noise_integ_off_pt)

        integ_window_pt = int((self.integ_window + eps) / dT)
        print(integ_window_pt)
        
        bin_width = dV * dT / mV / ns 

        print(bin_width)
        
        h_signal = ROOT.TH1D('signal', ';Integral Value (ns #times mV);Entries', 3500, -250.5 * bin_width, 3249.5 * bin_width)
        h_noise = ROOT.TH1D('noise', ';Integral Value (ns #times mV);Entries', 3500, -250.5 * bin_width, 3249.5 * bin_width)

        #make signal histogram
        for waveform in waveforms:
            for i_event in range(0, N_Event):
                t = waveform.xarray[i_event * N_pt_event : (i_event + 1) * N_pt_event] - waveform.xarray[i_event * N_pt_event]
                Vmax = np.amax(waveform.yarray[i_event * N_pt_event + integ_off_pt - integ_window_pt : i_event * N_pt_event + integ_off_pt])
                Vmin = np.amin(waveform.yarray[i_event * N_pt_event + integ_off_pt - integ_window_pt : i_event * N_pt_event + integ_off_pt])
                
                if Vmax - Vmin >= 5 * mV:
                    continue

                V = waveform.yarray[i_event * N_pt_event : (i_event + 1) * N_pt_event] - np.mean(waveform.yarray[i_event * N_pt_event + integ_off_pt - integ_window_pt : i_event * N_pt_event + integ_off_pt])
                
                peak_integ = V[integ_off_pt : integ_off_pt + integ_window_pt].sum() * dT

                h_signal.Fill(peak_integ / (ns * mV))


        #make noise histogram
        for waveform in waveforms:
            for i_event in range(0, N_Event):
                t = waveform.xarray[i_event * N_pt_event : (i_event + 1) * N_pt_event] - waveform.xarray[i_event * N_pt_event]
                Vmax = np.amax(waveform.yarray[i_event * N_pt_event + noise_integ_off_pt - integ_window_pt : i_event * N_pt_event + noise_integ_off_pt])
                Vmin = np.amin(waveform.yarray[i_event * N_pt_event + noise_integ_off_pt - integ_window_pt : i_event * N_pt_event + noise_integ_off_pt])
                
                if Vmax - Vmin >= 5 * mV:
                    continue

                V = waveform.yarray[i_event * N_pt_event : (i_event + 1) * N_pt_event] - np.mean(waveform.yarray[i_event * N_pt_event + noise_integ_off_pt - integ_window_pt : i_event * N_pt_event + noise_integ_off_pt])
                
                noise_integ = V[noise_integ_off_pt : noise_integ_off_pt + integ_window_pt].sum() * dT

                h_noise.Fill(noise_integ / (ns * mV))

        self.hist = h_signal.Clone()
        self.nhist = h_noise.Clone()
        self.hist.SetDirectory(0)
        self.nhist.SetDirectory(0)
        del h_signal
        del h_noise


        

    def Save_Hist(self):
        dirname = '%s' % self.name
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        hfile = ROOT.TFile('%s/ch%d_%s.root' % (self.name, self.channel, self.angle), "recreate")
        self.hist.Write()
        self.nhist.Write()
        hfile.Close()
      
