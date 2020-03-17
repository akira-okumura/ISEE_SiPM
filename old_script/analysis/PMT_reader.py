#
#Script for making histograms from PMT data
#integ_off and integ_window have to be adjusted for each dataset
#PMT(ch*_/extension/, channel, create new, folder name)
#
import numpy as np
import isee_sipm
import math
import ROOT
import sys
import os

s = 1 # (s)
ms = 1e-3 * s # (ms)
us = 1e-6 * s # (us)
ns = 1e-9 * s # (ns)

V = 1 # (V)
mV = 1e-3 * V # (mV)

class PMT:
    def __init__(self, dataset, ch, create, name = 'hists', integ_off = 433 * ns):
        self.nominal_period = 500*ns # approximate period
        self.integ_off = integ_off
        self.name = name
        self.mean = 0
        self.dset = dataset
        self.channel = ch
        self.meanerror = 0
        self.fname = ''
        self.hist = ROOT.TH1D()
        self.nhist = ROOT.TH1D()
        if create != 0:
            self.hist_wave(dataset, ch)
        if create == 0:
            self.OpenHist()
        self.Ppeak = 0 #Pedestal mean
        self.Opeak = 0 #One PE mean
        self.Ppeak_err = 0
        self.Opeak_err = 0




    def hist_wave(self, dataset, ch):
        fch = 'ch%d_%s.txt.gz'%(ch, dataset)
        self.fname = fch
        wave_ch1 = isee_sipm.gzip2waveforms(fch)
        nwaveforms = len(wave_ch1)


        dV = wave_ch1[0].get_dv() # quantized delta V in (V)
        dT = wave_ch1[0].get_dt() # sampling period 0.5 ns for 2 GHz sampling
    ##

        npt = wave_ch1[0].get_n() # sampling points per waveform
        eps = 0.001 * ns
        n_per = int(float(npt)*dT/self.nominal_period)
        npt_per = int(self.nominal_period/dT)
        self.integ_off = 433 * ns # integration offset from trigger
        integ_off_pt = int((self.integ_off + eps) / dT)
        noise_integ_off = self.integ_off - 100 * ns # integration offset from trigger
        noise_integ_off_pt = int((noise_integ_off + eps) / dT)
        integ_window = 20 * ns # peak width
        integ_window_pt = int((integ_window + eps)/dT)
        bin_width = dV * dT / mV / ns
##        print('bin width = %f'%bin_width)
        h_spec1 = ROOT.TH1D('signal', ';Integral Value (ns #times mV);Entries',
                            3500, -250.5 * bin_width , 3249.5 * bin_width)
        h_spec2 = ROOT.TH1D('noise', ';Integral Value (ns #times mV);Entries',
                            3500, -250.5 * bin_width , 3249.5 * bin_width)
    ##    print(n_per)
    ##
    ##
        for i in range(0, nwaveforms):
            for ievt in range(0, n_per-1):
                t = wave_ch1[i].xarray[ievt*npt_per: (ievt+1)*npt_per] - wave_ch1[i].xarray[ievt*npt_per]
    ##            V = wave_ch1[i].yarray[ievt*npt_per: (ievt+1)*npt_per]
                Vmax = np.amax(wave_ch1[i].yarray[ievt*npt_per + integ_off_pt - integ_window_pt: ievt*npt_per + integ_off_pt])
                Vmin = np.amin(wave_ch1[i].yarray[ievt*npt_per + integ_off_pt - integ_window_pt: ievt*npt_per + integ_off_pt])
##                print('Vdiff = %f; 1 mV = %f' %(Vmax - Vmin, mV))
                if Vmax - Vmin >= 5 * mV:
                    continue
                V = wave_ch1[i].yarray[ievt*npt_per: (ievt+1)*npt_per] - np.mean(wave_ch1[i].yarray[ievt*npt_per + integ_off_pt - integ_window_pt: ievt*npt_per + integ_off_pt])
                peak_integ1 = V[integ_off_pt : integ_off_pt + integ_window_pt].sum()*dT
##                print(peak_integ1/(dT*dV))
                h_spec1.Fill(peak_integ1/(ns*mV))

        for i in range(0, nwaveforms):
            for ievt in range(0, n_per-1):
                t = wave_ch1[i].xarray[ievt*npt_per: (ievt+1)*npt_per] - wave_ch1[i].xarray[ievt*npt_per]
    ##            V = wave_ch1[i].yarray[ievt*npt_per: (ievt+1)*npt_per]
                Vmax = np.amax(wave_ch1[i].yarray[ievt*npt_per + noise_integ_off_pt - integ_window_pt: ievt*npt_per + noise_integ_off_pt])
                Vmin = np.amin(wave_ch1[i].yarray[ievt*npt_per + noise_integ_off_pt - integ_window_pt: ievt*npt_per + noise_integ_off_pt])
##                print('Vdiff = %f; 1 mV = %f' %(Vmax - Vmin, mV))
                if Vmax - Vmin >= 5 * mV:
                    continue
                V = wave_ch1[i].yarray[ievt*npt_per: (ievt+1)*npt_per] - np.mean(wave_ch1[i].yarray[ievt*npt_per + noise_integ_off_pt - integ_window_pt: ievt*npt_per + noise_integ_off_pt])
                noise_integ = V[noise_integ_off_pt : noise_integ_off_pt + integ_window_pt].sum()*dT
##                print(peak_integ1/(dT*dV))
                h_spec2.Fill(noise_integ/(ns*mV))

        self.hist = h_spec1.Clone()
        self.nhist = h_spec2.Clone()
        self.hist.SetDirectory(0)
        self.nhist.SetDirectory(0)
        del h_spec1
        del h_spec2


    def GetMean(self):
        return self.hist.GetMean()
    def GetError(self):
        return self.hist.GetMeanError()
    def GetHist(self):
        return self.hist
    def GetFname(self):
        return self.fname
    def SaveHist(self):
        dirname = '%s'%self.name
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        hfile1 = ROOT.TFile('%s/ch%d_%s.root'%(self.name, self.channel, self.dset), "recreate")
        self.hist.Write()
        self.nhist.Write()
        hfile1.Close()
    def OpenHist(self):
        hfile1 = ROOT.TFile('%s/ch%d_%s.root'%(self.name, self.channel, self.dset))
        self.hist = hfile1.Get('signal')
        self.hist.SetDirectory(0)
        self.nhist = hfile1.Get('noise')
        self.nhist.SetDirectory(0)
        hfile1.Close()
        return

    def fit_0(self):
        ntotal = self.hist.GetEntries()
        fit_fun = ROOT.TF1("fit","[0]*exp(-0.5*((x - [1])/[2])**2)", -10, 5)
        #0 pe
        fit_fun.SetParName(0, 'N0')
        fit_fun.SetParName(1, 'mean0')
        fit_fun.SetParName(2, 'sigma0')
        fit_fun.SetParLimits(0,0, 0.9*ntotal)
        fit_fun.SetParLimits(1,-10, 5)
        fit_fun.SetParLimits(2, 2, 50)
        fit_fun.SetParameter(0, 0.5*ntotal)
        fit_fun.SetParameter(1,0)
        fit_fun.SetParameter(2,3)


        fit = self.hist.Fit(fit_fun,'S',"",-10.,5.)
        self.Ppeak = fit_fun.GetParameter(1)
        self.Ppeak_err = fit_fun.GetParError(1)
        return

    def fit_1(self):
        ntotal = self.hist.GetEntries()
        fit_fun = ROOT.TF1("fit","[0]*exp(-0.5*((x - [1])/[2])**2)", 13, 33)
        #0 pe
        fit_fun.SetParName(0, 'N0')
        fit_fun.SetParName(1, 'mean0')
        fit_fun.SetParName(2, 'sigma0')
        fit_fun.SetParLimits(0,0, 0.9*ntotal)
        fit_fun.SetParLimits(1, 13, 33)
        fit_fun.SetParLimits(2, 2, 50)
        fit_fun.SetParameter(0, 0.5*ntotal)
        fit_fun.SetParameter(1, 25)
        fit_fun.SetParameter(2, 3)



        fit = self.hist.Fit(fit_fun,'S',"", 13., 33.)
        self.Opeak = fit_fun.GetParameter(1)
        self.Opeak_err = fit_fun.GetParError(1)
        return
    def GetGain(self):
        self.fit_0()
        self.fit_1()
        return self.Opeak - self.Ppeak
    def GetGainError(self):
        return np.sqrt(np.power(self.Ppeak_err,2) + np.power(self.Opeak_err,2))
##    def ShiftZero(self):
##        self.hist.GetXaxis().SetRange(self.hist.FindBin(-40.), self.hist.FindBin(0.))
##        peak = self.hist.GetMaximum()
##        shift = peak - self.hist.FindBin(0.)


##pmt = PMT(dataset)
