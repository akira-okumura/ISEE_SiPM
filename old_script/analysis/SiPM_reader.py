'''
creates histograms
'''
import target_driver
import target_io
import numpy as np
import argparse
import scipy.io
from tqdm import tqdm
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


class SiPM:
    def __init__(self, filename, asic, channel, create):
        self.filename = filename
        self.asic = asic
        self.channel = channel
        self.hSignal = ROOT.TH1D
        self.hNoise = ROOT.TH1D
        if create == 0:
            dirname = filename
            hfile = ROOT.TFile("%s/hist_as%d_ch%d.root" %(dirname, self.asic, self.channel))
            self.hNoise = hfile.Get('noise').Clone()
            self.hSignal = hfile.Get('signal').Clone()
            self.hNoise.SetDirectory(0)
            self.hSignal.SetDirectory(0)
            hfile.Close()


    def makehist(self):
        # dv and dt
        dV = 1.454170273973432 * 1e-6
        dT = 1 * ns
        bin_width = dV * dT / mV / ns * 750

        self.hNoise = ROOT.TH1D("noise","noise;Charge (mV #times ns);", 1000, -299.5 * bin_width, 700.5 * bin_width)
        self.hSignal = ROOT.TH1D("signal","signal;Charge (mV #times ns);", 1000, -299.5 * bin_width, 700.5 * bin_width)
        print('\nanalyzing a%d ch%d'%(self.asic,self.channel))

        # Time window for integration. integral +/- 6 ns around the peak
        tw = 12
        NSamples = 14*32
        sample0=0
        chann = self.channel + self.asic*16
    ##    print(chann)
        reader = target_io.EventFileReader(self.filename)
        NEvents  = reader.GetNEvents()
        useEvents = NEvents
        print("found %d events, using %d events"%(NEvents, useEvents))
        ampl = np.zeros([NEvents,NSamples])

        # Directory of transfer functions
        tf_filename = '/Users/az/CTA/work/PMT_SiPM_Nagoya/target/TF/new_run/mat/tf_chan%d.mat' % chann
        mat_tf = scipy.io.loadmat(tf_filename)

        for ievt in tqdm(range(0, useEvents)):
            rawdata = reader.GetEventPacket(ievt,chann)
            packet = target_driver.DataPacket()
            packet.Assign(rawdata, reader.GetPacketSize())
            wf = packet.GetWaveform(0)

            for sample in range(0, NSamples):
                ampl[ievt,sample] = mat_tf.get('TFs')[sample, wf.GetADC(sample0+sample)]

            # Fill noise
        for ievt in tqdm(range(0, useEvents)):
            t_peak = 190
            charge = 0.
            mean = np.mean(ampl[ievt, t_peak - 50 : t_peak])
            stdev = np.std(ampl[ievt, t_peak - 50 : t_peak])
            if (np.amax(ampl[ievt, t_peak - 50 : t_peak]) - np.amin(ampl[ievt, t_peak - 50 : t_peak]) > 10):
                continue
            # charge = np.sum(ampl[ievt, t_peak : t_peak + 2 * tw]) - mean * tw * 2
            for cell in range(t_peak, t_peak + 2 * tw):
                if ampl[ievt, cell] >= mean - 2 * stdev:
                    charge += ampl[ievt, cell]
                else:
                    charge += mean
            charge -= mean * tw * 2
            self.hNoise.Fill(charge)

            # Fill signal
        for ievt in tqdm(range(0, useEvents)):
            t_peak = 297
            charge = 0.
            mean = np.mean(ampl[ievt, t_peak - 50 : t_peak])
            stdev = np.std(ampl[ievt, t_peak - 50 : t_peak])
            if (np.amax(ampl[ievt, t_peak - 50 : t_peak]) - np.amin(ampl[ievt, t_peak - 50 : t_peak]) > 10):
                continue
            # charge = np.sum(ampl[ievt, t_peak : t_peak + 2 * tw]) - mean * tw * 2
            for cell in range(t_peak, t_peak + 2 * tw):
                if ampl[ievt, cell] >= mean - 2 * stdev:
                    charge += ampl[ievt, cell]
                else:
                    charge += mean
            charge -= mean * tw * 2
            self.hSignal.Fill(charge)



        # Output
        dirname = 'hists'
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        dirname = '%s/%s' % (dirname, self.filename[:-5])
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        hfile = ROOT.TFile("%s/hist_as%d_ch%d.root" %(dirname, self.asic, self.channel), "recreate")
        self.hNoise.Write()
        self.hSignal.Write()
        hfile.Close()
        return

    def GetNoise(self):
        return self.hNoise

    def GetSignal(self):
        return self.hSignal



    ##    h.Draw()
    ##    c.Update()
    ##    c.Print('test.pdf')
    ##    return H0

    #
    # NSamples = 448
    # if __name__=="__main__":
    #
    #     args = sys.argv
    #     noise = int(args[1])
    #
    #     an_part0 = np.array([40,37])
    #     an_part1 = np.arange(35,18,-1)
    #     an_part2 = np.arange(18,-3,-3)
    #     angles = np.concatenate((an_part0, an_part1, an_part2))
    # ##    index = np.argwhere(angles == 27)
    # ##    index = index[0][0]
    #
    # ##    angles = np.arange(-24,41)
    # for i in range(0,angles.size):
    #     filename = "3800_1000_5_%ddeg.fits"%angles[i]
    #     print(filename)
    #     for i in range(0,4):
    #         for j in range(0,16):
    #             ChargeSpectrum(filename, NSamples, i, j, noise)
