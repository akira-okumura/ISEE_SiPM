import target_driver
import target_io
import matplotlib.pyplot as plt
import numpy as np
import pdb
import argparse
import scipy.io
import scipy.interpolate
from scipy.signal import wiener, medfilt
from tqdm import tqdm
import math
import ROOT
import sys


def plot_wave(filename, asic, channel):

    c = ROOT.TCanvas()
    graph = ROOT.TGraph()
            
    Vped = 900
    Vped = (0.021 + 0.0006*Vped) * 1000
    
    NSamples = 14*32
    sample0=0
    chann = channel + asic*16
    print(chann)
    reader = target_io.EventFileReader(filename)
    NEvents  = reader.GetNEvents()
    useEvents = NEvents
    print("found %d events, using %d events"%(NEvents, useEvents))
    ampl = np.zeros([NEvents,NSamples])
    
    # Directory of transfer functions
    tf_filename = '/Users/az/CTA/work/PMT_SiPM_Ibaraki/data/transfer_fun/TF/tf_chan%d.mat' % chann
    mat_tf = scipy.io.loadmat(tf_filename)
    
    for ievt in range(0, useEvents):
        rawdata = reader.GetEventPacket(ievt,chann)
        packet = target_driver.DataPacket()
        packet.Assign(rawdata, reader.GetPacketSize())

        wf = packet.GetWaveform(0)
         

        
        for sample in range(0, NSamples):
            ampl[ievt,sample] = mat_tf.get('invertedTFs')[sample, wf.GetADC(sample0+sample)]
            V = ampl[ievt, sample]

            graph.SetPoint(sample, sample, V)


        graph.SetTitle("")
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(0.3)
        graph.GetXaxis().SetTitle("cell number")
        graph.GetYaxis().SetTitle("Voltage (mV)")

        graph.GetXaxis().SetLimits(0,NSamples)

        graph.Draw("apl")

        graph.GetHistogram().GetXaxis().SetNdivisions(400+14,0)
        graph.GetYaxis().SetRangeUser(860, 930)

        c.SetGridx()
        c.SetGridy()

        c.Print("test2.pdf")

        input('input')
        
if __name__=="__main__":
    
    args = sys.argv
    filename = str(args[1])
    asic = int(args[2])
    channel = int(args[3])
    #ievt = int(args[4])
    
    plot_wave(filename, asic, channel)
    
