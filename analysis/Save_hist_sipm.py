import numpy as np
from tqdm import tqdm
import SiPM_reader
import ROOT
import sys
import os
import glob

angles = np.arange(-40, 41)

# sipm = SiPM_reader.SiPM('2500_0_4_0deg_fwd.fits', 0, 8, 1)
# sipm.makehist()

vhigh = 2500 #mV
vlow = 0 #mV
width = 4 #ns

if not os.path.exists('SavedGraph'):
    os.mkdir('SavedGraph')
    
file_list = sorted(glob.glob("*.fits"))
print(file_list)

ASIC_num = [37,36,33,32,53,52,49,48,39,38,35,34,55,54,51,50,45,44,41,40,61,60,57,56,47,46,43,42,63,62,59,58,10,11,14,15,26,27,30,31,8,9,12,13,24,25,28,29,2,3,6,7,18,19,22,23,0,1,4,5,16,17,20,21]

'''
for k in tqdm(range(len(angles))):
    for i in tqdm(range(4)):
        print('======= start: %d deg ========' % angles[k])
        for j in tqdm(range(16)):
            sipm = SiPM_reader.SiPM('test/data0311/%d_%d_%d_%ddeg_fwd.fits' % (vhigh, vlow, width, angles[k]), i, j)
            sipm.makehist()
'''

for file_n in tqdm(file_list, desc = "file"):
    c_waveform = ROOT.TCanvas(file_n + "waveform", file_n + "waveform", 1500, 1500)
    c_peaktime = ROOT.TCanvas(file_n + "peaktime", file_n + "peaktime", 1500, 1500)
    c_hists = ROOT.TCanvas(file_n + "signal", file_n + "signal", 1500, 1500)
    c_histn = ROOT.TCanvas(file_n + "noise", file_n + "noise", 1500, 1500)

    c_waveform.Divide(8,8)
    c_peaktime.Divide(8,8)
    c_hists.Divide(8,8)
    c_histn.Divide(8,8)
    for i in tqdm(range(4), leave = False, desc = "asic"):
        for j in tqdm(range(16), leave = False, desc = "CH"):
            
            sipm = SiPM_reader.SiPM(file_n, i, j)
            sipm.makehist()

            
                        
            cd_num = ASIC_num.index(i * 16 + j) + 1
            c_hists.cd(cd_num)
            hists_g = sipm.GetSignal()
            hists_g.Draw()
            c_hists.cd(cd_num).SetGridx()
            c_hists.cd(cd_num).SetLogy()

            c_histn.cd(cd_num)
            histn_g = sipm.GetNoise()
            histn_g.Draw()
            c_histn.cd(cd_num).SetGridx()
            c_histn.cd(cd_num).SetLogy()

            c_peaktime.cd(cd_num)
            peaktime_g = sipm.GetPeaktime()
            peaktime_g.Draw()
            peaktime_g.GetXaxis().SetLabelSize(0.07)
            peaktime_g.GetYaxis().SetLabelSize(0.07)

            textp = ROOT.TLatex()
            textp.SetTextSize(0.1)
            textp.DrawLatex(5, 1500, "peak:%s" % str(peaktime_g.GetMaximumBin()))

            #### 生波形の描画 ####
            wave = sipm.GetGwaveform()
            c_waveform.cd(cd_num)
            frame = c_waveform.cd(cd_num).DrawFrame(0, 870, 448, 1000)
            frame.GetXaxis().SetNdivisions(510)
            frame.GetXaxis().SetLabelSize(0.07)
            
            #for wi in range(len(wave))
            for wi in range(10):
                wave[wi].SetLineColor(wi % 9)
                wave[wi].Draw("l")

            c_waveform.cd(cd_num).SetGridx()

            sipm.DellHist()
            del sipm

    c_waveform.Update()
    c_peaktime.Update()
    c_hists.Update()
    c_histn.Update()

    c_waveform.SaveAs("SavedGraph/"+file_n+"_waveform.root")
    c_waveform.Print("SavedGraph/"+file_n+"_waveform.pdf", 'pdf Portrait')
    c_peaktime.SaveAs("SavedGraph/"+file_n+"_peaktime.root")
    c_peaktime.Print("SavedGraph/"+file_n+"_peaktime.pdf", 'pdf Portrait')
    c_hists.SaveAs("SavedGraph/"+file_n+"_signal.root")
    c_hists.Print("SavedGraph/"+file_n+"_signal.pdf", 'pdf Portrait')
    c_histn.SaveAs("SavedGraph/"+file_n+"_noise.root")
    c_histn.Print("SavedGraph/"+file_n+"_noise.pdf", 'pdf Portrait')
    
