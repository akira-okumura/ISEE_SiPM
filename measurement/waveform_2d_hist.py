'''
Make charge spectrum
Y. Nakamura

How to use:
python MakeChargeSpectrum.py --filename xxx.fits --asic 0 --channel 0 --n_samples 448
'''
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
import ROOT

def ChargeSpectrum(filename, NSamples, asic, channel):

  ##  c = ROOT.TCanvas()
    graph = ROOT.TGraph()
##    h = ROOT.TH1D("h","h;Charge (mV * ns);", 400, 9000, 13000)
    h = ROOT.TH1D("h","h;Charge (mV #times ns);", 150, -500, 1000)
  
    h2d = ROOT.TH2D("h2d", ";time (ns); Voltage (mV)", 448, 0, 448, 2000, -1000, 1000)
##    c.SetLogy()

    # Time window for integration. integral +/- 6 ns around the peak
    tw = 6


    #tf_filename = '/Users/az/CTA/work/PMT_SiPM_Nagoya/target/TF/new_run/mat/tf_chan%d.mat' % channel
    tf_filename = '/Volumes/Untitled/kuroda/2020target/transfer_fun/TF/mat/tf_chan%d.mat' % channel
    mat_tf = scipy.io.loadmat(tf_filename)

    reader = target_io.EventFileReader(filename)
    # NEvents = reader.GetNEvents()
    NEvents = 20000
    sample0 = 0
    ampl = np.zeros([NEvents,NSamples])
    x = np.arange(NSamples)

    # Directory of transfer functions

    for ievt in tqdm(range(NEvents)):
        rawdata = reader.GetEventPacket(ievt,channel)
        packet = target_driver.DataPacket()
        packet.Assign(rawdata, reader.GetPacketSize())

        wf = packet.GetWaveform(0)

        for sample in range(NSamples):
            ampl[ievt,sample] = mat_tf.get('TFs')[sample, wf.GetADC(sample0+sample)]
        for sample in range(NSamples):
            h2d.Fill(sample, ampl[ievt,sample]-np.mean(ampl[ievt,0:250]))

        ##Peak should be around 300 ns, because LED flashed there
        #t_peak = np.argmax(ampl[300:320]) + 300
    
        #h.Fill(np.sum(ampl[t_peak - tw : t_peak + tw]) - (np.mean(ampl[0:250])*tw*2))
        ##Output
    #h.Draw()
    #c.Update()
    #c.Print('test.pdf')
    return h2d

parser = argparse.ArgumentParser()
parser.add_argument("-a" ,"--asic", help="asic to be displayed", type=int, default="0")
parser.add_argument("-c" ,"--channel", help="Channel to be displayed", type=int, default="0")
parser.add_argument("-f" ,"--filename", help="File name", type=str, default="test.fits")

args = parser.parse_args()

NSamples = 14*32
asic = args.asic
channel = args.channel

filename = args.filename
print("%s"%filename)
c = ROOT.TCanvas()
his = ChargeSpectrum(filename, NSamples, asic, channel)

##c.SetLogy()
his.Draw("COLZ")
c.Update()
##input("pause")
