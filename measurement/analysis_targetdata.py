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
import glob

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

            self.hNoise = hfile.Get('noise%s.fits %d %d;1' % (self.filename.replace("hists/", ""), self.asic, self.channel)).Clone()
            self.hSignal = hfile.Get('signal%s.fits %d %d;1' % (self.filename.replace("hists/", ""), self.asic, self.channel)).Clone()
            self.hNoise.SetDirectory(0)
            self.hSignal.SetDirectory(0)
            hfile.Close()


    def makehist(self):
        # dv and dt
        dV = 1.454170273973432 * 1e-6
        dT = 1 * ns
        bin_width = dV * dT / mV / ns * 750

        # Time window for integration. integral +/- 6 ns around the peak
        tw = 12
        NSamples = 14*32
        sample0=0
        chann = self.channel + self.asic*16
    ##    print(chann)
        reader = target_io.EventFileReader(self.filename)
        NEvents  = reader.GetNEvents()
        useEvents = NEvents
        #print("found %d events, using %d events"%(NEvents, useEvents))
        ampl = np.zeros([NEvents,NSamples])

        self.g_waveform = []
        self.hpeaktime = ROOT.TH1D("peaktime%s %d %d" % (self.filename, self.asic, self.channel),"peaktime;time (ns);", NSamples + 1 , -0.5, NSamples + 0.5)
        self.hNoise = ROOT.TH1D("noise%s %d %d" % (self.filename, self.asic, self.channel),"noise;Charge (mV #times ns);", 1000, -299.5 * bin_width, 700.5 * bin_width)
        self.hSignal = ROOT.TH1D("signal%s %d %d" % (self.filename, self.asic, self.channel),"signal;Charge (mV #times ns);", 1000, -299.5 * bin_width, 700.5 * bin_width)

        # Directory of transfer functions #############################################################################
        tf_filename = '/Volumes/Untitled/kuroda/2020target/transfer_fun/TF/mat/tf_chan%d.mat' % chann  ########### tf file のディレクトリを指定する
        mat_tf = scipy.io.loadmat(tf_filename)

        for ievt in tqdm(range(0, useEvents), leave = False, desc = "Events"):
            rawdata = reader.GetEventPacket(ievt,chann)
            packet = target_driver.DataPacket()
            packet.Assign(rawdata, reader.GetPacketSize())
            wf = packet.GetWaveform(0)

            for sample in range(0, NSamples):
                ampl[ievt,sample] = mat_tf.get('TFs')[sample, wf.GetADC(sample0+sample)]

            # Fill noise

        count_wave = 0
        for ievt in tqdm(range(0, useEvents), leave = False, desc = "Events"):
            max_bin = np.argmax(ampl[ievt])
            self.hpeaktime.Fill(max_bin)
            ################################# 生波形の抽出 #################################################################
            #if 360 > max_bin > 280 and count_wave < 50 :  ###################### ここで、描画する生波形を取得するための条件を指定する
            self.g_waveform.append( ROOT.TGraph(NSamples,np.arange(NSamples)*1.0, ampl[ievt]) )
            count_wave += 1


        for ievt in tqdm(range(0, useEvents), leave = False, desc = "Events"):
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
        for ievt in tqdm(range(0, useEvents), leave = False, desc = "Events"):
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

    def DellHist(self):
        del self.hSignal
        del self.hNoise
        del self.g_waveform
        del self.hpeaktime

    def GetPeaktime(self):
        return self.hpeaktime

    def GetGwaveform(self):
        return self.g_waveform

class PEdistr:
    def __init__(self, dataset):
        self.p0_list = []
        self.p1_list = []
        self.Lam_list = []
        self.stat_error = 0
        self.sys_error = 0
        self.plambda = 0
        self.dataset = str(dataset)
        self.hist = ROOT.TH1D('','', 100, -0.2, 0.2)
        self.distr = ROOT.TH1D('','', 64, 0, 64)
        self.CalcLambda()
    def GetStatError(self):
        return self.stat_error
    def GetSysError(self):
        return self.sys_error
    def GetLambda(self):
        return self.plambda
    def Reset(self):
        self.stat_error = 0
        self.sys_error = 0
        self.plambda = 0
        self.dataset = ''
    def CalcLambda(self):
        for asic in range(0,4):
            for channel in range(0,16):
                sipm = SiPM(self.dataset, asic, channel, 0)
                hist_s = sipm.GetSignal().Clone()
                hist_n = sipm.GetNoise().Clone()
                #
                # min = hist_s.GetXaxis().GetXmin()
                # max = hist_s.GetXaxis().GetXmax()

                hist_s.GetXaxis().SetRangeUser(-40, 100)
                p0 = hist_s.GetMaximumBin()
                hist_s.GetXaxis().SetRangeUser(120, 250)
                p1 = hist_s.GetMaximumBin()
##                hist_s.GetXaxis().SetRange(p0,p1)
##                thrsh = hist_s.GetMinimumBin()
                thrsh = int((p0+p1)/1.9)
                # print("a %d, c %d, th %f" % (asic, channel, hist_s.GetBinCenter(thrsh)))
            ##    print(thrsh)
            ##    print(hist_s.FindBin(100))
                del hist_s
                del hist_n
                hist_s = sipm.GetSignal()
                hist_n = sipm.GetNoise()
                N0_s = hist_s.Integral(1,thrsh)
                N0_su = hist_s.Integral(1,hist_s.FindBin(hist_s.GetXaxis().GetBinCenter(thrsh) + 30))
                N0_sl = hist_s.Integral(1,hist_s.FindBin(hist_s.GetXaxis().GetBinCenter(thrsh) - 30))

                N0_n = hist_n.Integral(1,thrsh)
                N0_nu = hist_n.Integral(1,hist_n.FindBin(hist_n.GetXaxis().GetBinCenter(thrsh) + 30))
                N0_nl = hist_n.Integral(1,hist_n.FindBin(hist_n.GetXaxis().GetBinCenter(thrsh) - 30))

        ##        print(N0_sl/N0_su)
                N_s = hist_s.Integral() + hist_s.GetBinContent(hist_s.GetNbinsX() + 1)
                N_n = hist_n.Integral() + hist_n.GetBinContent(hist_n.GetNbinsX() + 1)

                P0_s = N0_s/N_s
                P0_su = N0_su/N_s
                P0_sl = N0_sl/N_s

                P0_n = N0_n/N_n
                P0_nu = N0_nu/N_n
                P0_nl = N0_nl/N_n

                err_s_stat = np.sqrt(N_s * (1 - P0_s) * P0_s) / N0_s
                err_n_stat = np.sqrt(N_n * (1 - P0_n) * P0_n) / N0_n


                err_s_sys = ROOT.TMath.Log(P0_sl) - ROOT.TMath.Log(P0_su)
                err_n_sys = ROOT.TMath.Log(P0_nl) - ROOT.TMath.Log(P0_nu)

        ##        print(err_n_stat/ROOT.TMath.Log(P0_n))
                err_tot_sys = np.sqrt(np.power(err_s_sys, 2) + np.power(err_n_sys, 2))
                err_tot_stat = np.sqrt(np.power(err_s_stat, 2) + np.power(err_n_stat, 2))

                self.sys_error += np.power(err_tot_sys,2)

                self.stat_error += np.power(err_tot_stat,2)
        ##        print(self.error)

                Plambda = - (ROOT.TMath.Log(P0_s) - ROOT.TMath.Log(P0_n))
                # print("a %d, c %d, P0s %f, P0n %f, lambda %f" % (asic, channel, P0_s, P0_n, Plambda))
        ##        print(err_tot/output[0]*100)
                self.plambda += Plambda
                self.hist.Fill(Plambda)
                self.distr.Fill(asic * 16 + channel, Plambda)
                self.p0_list.append(p0)
                self.p1_list.append(p1)
                self.Lam_list.append(Plambda)
                hist_s.Delete()
                hist_n.Delete()
                del sipm
        self.stat_error = np.sqrt(self.GetStatError())
        self.sys_error = np.sqrt(self.GetSysError())

    def GetLambdaHist(self):
        return self.hist
    def GetLambdaDistr(self):
        return self.distr

    def GetP0List(self):
        return self.p0_list

    def GetP1List(self):
        return self.p1_list

    def GetLamList(self):
        return self.Lam_list


if not os.path.exists('SavedGraph'):
    os.mkdir('SavedGraph')

#file_list = ['2500_0_4_00deg_fwd.fits']
file_list = sorted(glob.glob("*.fits"))
#file_list.remove('2500_0_4_00deg_fwd.fits')
print(file_list)

ASIC_num = [37,36,33,32,53,52,49,48,39,38,35,34,55,54,51,50,45,44,41,40,61,60,57,56,47,46,43,42,63,62,59,58,10,11,14,15,26,27,30,31,8,9,12,13,24,25,28,29,2,3,6,7,18,19,22,23,0,1,4,5,16,17,20,21]

# create canvas (divide 8,8)
c_waveform = [ ROOT.TCanvas(file_list[i]+"waveform%s"%str(i),file_list[i]+"waveform%s"%str(i),1500,1500) for i in range(len(file_list)) ]
c_peaktime = [ ROOT.TCanvas(file_list[i]+"peaktime%s"%str(i),file_list[i]+"peaktime%s"%str(i),1500,1500) for i in range(len(file_list)) ]
c_hists = [ ROOT.TCanvas(file_list[i]+"signal%s"%str(i),file_list[i]+"signal%s"%str(i),1500,1500) for i in range(len(file_list)) ]
c_histn = [ ROOT.TCanvas(file_list[i]+"noise%s"%str(i),file_list[i]+"noise%s"%str(i),1500,1500) for i in range(len(file_list)) ]

for i in range(len(file_list)):
    c_waveform[i].Divide(8,8)
    c_peaktime[i].Divide(8,8)
    c_hists[i].Divide(8,8)
    c_histn[i].Divide(8,8)

# create Tgraph , TH1D for 64ch
peaktime_g = [ROOT.TH1D() for i in range( (len(file_list) + 1) * 64)]
hists_g = [ROOT.TH1D() for i in range( (len(file_list) + 1) * 64)]
histn_g = [ROOT.TH1D() for i in range( (len(file_list) + 1) * 64)]
wave = [ [] for i in range( (len(file_list) + 1) * 64)]

i_file = 0

for file_n in tqdm(file_list, desc = "file len = %d" % len(file_list)):

    #continue #ヒストグラムの計算をスキップするとき

    #print('======= start: %s file ========' % file_n)
    for i in tqdm(range(4), leave = False, desc = "asic"):
        #print('------- start: %d / 4 asic ========' % (i+1))
        for j in tqdm(range(0, 16, 1), leave = False, desc = "channel"):

            g_num = i_file*64 + i * 16 + j

            sipm = SiPM(file_n, i, j, 1)
            sipm.makehist()

            #Draw histgram
            cd_num = ASIC_num.index(i*16 + j) + 1
            c_hists[i_file].cd(cd_num)
            hists_g[g_num] = sipm.GetSignal()
            hists_g[g_num].Draw()
            c_hists[i_file].cd(cd_num).SetGridx()
            c_hists[i_file].cd(cd_num).SetLogy()

            c_histn[i_file].cd(cd_num)
            histn_g[g_num] = sipm.GetNoise()
            histn_g[g_num].Draw()
            c_histn[i_file].cd(cd_num).SetGridx()
            c_histn[i_file].cd(cd_num).SetLogy()

            c_peaktime[i_file].cd(cd_num)
            peaktime_g[g_num] = sipm.GetPeaktime()
            peaktime_g[g_num].Draw()
            peaktime_g[g_num].GetXaxis().SetLabelSize(0.07)
            peaktime_g[g_num].GetYaxis().SetLabelSize(0.07)
            textp = ROOT.TLatex()
            textp.SetTextSize(0.1)
            textp.DrawLatex( 5 , 1500 , "peak:%s"%str(peaktime_g[g_num].GetMaximumBin() ) )


            ################ 生波形の描画 ###################################################
            wave[g_num] = sipm.GetGwaveform()
            c_waveform[i_file].cd(cd_num)

            #for wi in range(len(wave[g_num])):
            for wi in range(10):
               if wi == 0:
                   wave[g_num][wi].Draw("apl")
                   wave[g_num][wi].GetXaxis().SetNdivisions(510)
                   wave[g_num][wi].GetXaxis().SetLabelSize(0.07)
                   #wave[g_num][wi].GetXaxis().SetRangeUser(280,380)
                   wave[g_num][wi].GetYaxis().SetLabelSize(0.07)
                   wave[g_num][wi].GetYaxis().SetRangeUser(870,1000)

               else:
                   wave[g_num][wi].Draw("samel")
               wave[g_num][wi].SetLineColor(wi % 9)

            c_waveform[i_file].cd(cd_num).SetGridx()

            sipm.DellHist() #to avoid memory reak

            del sipm

        #print('======= finish: %d / 4 asic --------' % (i+1))
    #print('======= finish: %s file ========' % file_n)

    c_waveform[i_file].Update()
    c_peaktime[i_file].Update()
    c_hists[i_file].Update()
    c_histn[i_file].Update()

    c_waveform[i_file].SaveAs("SavedGraph/"+file_n+"_waveform.root")
    c_waveform[i_file].Print("SavedGraph/"+file_n+"_waveform.pdf", 'pdf Portrait')
    c_peaktime[i_file].SaveAs("SavedGraph/"+file_n+"_peaktime.root")
    c_peaktime[i_file].Print("SavedGraph/"+file_n+"_peaktime.pdf", 'pdf Portrait')
    c_hists[i_file].SaveAs("SavedGraph/"+file_n+"_signal.root")
    c_hists[i_file].Print("SavedGraph/"+file_n+"_signal.pdf", 'pdf Portrait')
    c_histn[i_file].SaveAs("SavedGraph/"+file_n+"_noise.root")
    c_histn[i_file].Print("SavedGraph/"+file_n+"_noise.pdf", 'pdf Portrait')

    i_file += 1


x_p = [0,1,0,1,2,3,2,3,0,1,0,1,2,3,2,3,4,5,4,5,6,7,6,7,4,5,4,5,6,7,6,7,3,2,3,2,1,0,1,0,3,2,3,2,1,0,1,0,7,6,7,6,5,4,5,4,7,6,7,6,5,4,5,4]
y_p = [0,0,1,1,0,0,1,1,2,2,3,3,2,2,3,3,0,0,1,1,0,0,1,1,2,2,3,3,2,2,3,3,7,7,6,6,7,7,6,6,5,5,4,4,5,5,4,4,7,7,6,6,7,7,6,6,5,5,4,4,5,5,4,4]

sipm_data = [ [] for i in range(len(file_list)) ]
h_Lam_Distr = [ [] for i in range(len(file_list)) ]
LamDistr_g = [ROOT.TH2D('', '; X pixel ; Y pixel ;', 8, -0.5, 7.5, 8, -0.5, 7.5) for i in range(len(file_list))]
p0_g = [ROOT.TH2D('', '; X pixel ; Y pixel ;', 8, -0.5, 7.5, 8, -0.5, 7.5) for i in range(len(file_list))]
p1_g = [ROOT.TH2D('', '; X pixel ; Y pixel ;', 8, -0.5, 7.5, 8, -0.5, 7.5) for i in range(len(file_list))]
p01_g = [ROOT.TH2D('', '; X pixel ; Y pixel ;', 8, -0.5, 7.5, 8, -0.5, 7.5) for i in range(len(file_list))]

ROOT.gStyle.SetPalette(1)

c_LamDistr = [ ROOT.TCanvas("Lambda_Distr%s"%str(i),"Lambda_Distr%s"%str(i),1500,1500) for i in range(int(len(file_list)/16) +1 ) ]
c_p0 = [ ROOT.TCanvas("P0_Distr%s"%str(i),"P0_Distr%s"%str(i),1500,1500) for i in range(int(len(file_list)/16) +1 ) ]
c_p1 = [ ROOT.TCanvas("P1_Distr%s"%str(i),"P1_Distr%s"%str(i),1500,1500) for i in range(int(len(file_list)/16) +1 ) ]
c_p01 = [ ROOT.TCanvas("P01_Distr%s"%str(i),"P01_Distr%s"%str(i),1500,1500) for i in range(int(len(file_list)/16) +1 ) ]
for i in range(int(len(file_list)/16) +1 ):
    c_LamDistr[i].Divide(4,4)
    c_p0[i].Divide(4,4)
    c_p1[i].Divide(4,4)
    c_p01[i].Divide(4,4)
    
i_file = 0

for file_n in tqdm(file_list):
    sipm_data[i_file] = PEdistr("hists/"+file_list[i_file].replace(".fits",""))


    can_num =  int(i_file/16)
    cd_num = i_file - can_num * 16 + 1

    c_LamDistr[can_num].cd(cd_num)
    Lam = sipm_data[i_file].GetLamList()
    for i in range(64):
        LamDistr_g[i_file].Fill(x_p[i],y_p[i],round(Lam[i],3))
        #print(file_n,x_p[i],y_p[i],round(Lam[i],2))
    LamDistr_g[i_file].Draw('TEXT COLZ')
    LamDistr_g[i_file].SetTitle(file_n + " Lam sum %s; X pixel ; Y pixel ; Lambda_pe"%str(round( sum(Lam) ,2)))
    LamDistr_g[i_file].SetMinimum(-0.3)
    LamDistr_g[i_file].SetMaximum(2)
    LamDistr_g[i_file].SetMarkerSize(2.3)
    ROOT.gStyle.SetOptStat(0)
    #LamDistr_g[i_file].GetXaxis().SetLimits(140.4,152.8)
    #LamDistr_g[i_file].GetXaxis().SetNdivisions(520)
    #LamDistr_g[i_file].GetXaxis().SetLabelSize(0.02)
    #LamDistr_g[i_file].GetYaxis().SetLimits(41.4,53.8)
    #LamDistr_g[i_file].GetYaxis().SetNdivisions(520)
    #LamDistr_g[i_file].GetYaxis().SetLabelSize(0.02)
    LamDistr_g[i_file].GetZaxis().SetNdivisions(530)
    #c_LamDistr[can_num].cd(cd_num).SetGridx()
    #c_LamDistr[can_num].cd(cd_num).SetGridy()
    c_LamDistr[can_num].cd(cd_num).Update()

    c_p0[can_num].cd(cd_num)
    P0 = sipm_data[i_file].GetP0List()
    for i in range(64):
        p0_g[i_file].Fill(x_p[i],y_p[i],round((P0[i] - 299.98)/0.917,1))
    p0_g[i_file].Draw('TEXT COLZ')
    p0_g[i_file].SetTitle(file_n + " P0; X pixel ; Y pixel ; p0_peak")
    p0_g[i_file].SetMinimum(-50)
    p0_g[i_file].SetMaximum(110)
    p0_g[i_file].SetMarkerSize(2.3)
    ROOT.gStyle.SetOptStat(0)
    p0_g[i_file].GetZaxis().SetNdivisions(530)
    c_p0[can_num].cd(cd_num).Update()

    c_p1[can_num].cd(cd_num)
    P1 = sipm_data[i_file].GetP1List()
    for i in range(64):
        p1_g[i_file].Fill(x_p[i],y_p[i],round((P1[i] - 299.98)/0.917,1))
    p1_g[i_file].Draw('TEXT COLZ')
    p1_g[i_file].SetTitle(file_n + " P1; X pixel ; Y pixel ; p1_peak")
    p1_g[i_file].SetMinimum(110)
    p1_g[i_file].SetMaximum(260)
    p1_g[i_file].SetMarkerSize(2.3)
    ROOT.gStyle.SetOptStat(0)
    p1_g[i_file].GetZaxis().SetNdivisions(530)
    c_p1[can_num].cd(cd_num).Update()

    c_p01[can_num].cd(cd_num)
    for i in range(64):
        p01_g[i_file].Fill(x_p[i],y_p[i],round(( (P0[i]+P1[i])/1.9 - 299.98)/0.917,1))
    p01_g[i_file].Draw('TEXT COLZ')
    p01_g[i_file].SetTitle(file_n + " P0+P1 / 1.9; X pixel ; Y pixel ; p0_peak")
    p01_g[i_file].SetMinimum(40)
    p01_g[i_file].SetMaximum(170)
    p01_g[i_file].SetMarkerSize(2.3)
    ROOT.gStyle.SetOptStat(0)
    p01_g[i_file].GetZaxis().SetNdivisions(530)
    c_p01[can_num].cd(cd_num).Update()

    i_file += 1

for i in range(int(len(file_list)/16) +1 ):
    c_LamDistr[i].SaveAs("SavedGraph/"+"Lambda%d.root"%i)
    c_LamDistr[i].Print("SavedGraph/"+"Lambda%d.pdf"%i, 'pdf Portrait')
    c_p0[i].SaveAs("SavedGraph/"+"p0%d.root"%i)
    c_p0[i].Print("SavedGraph/"+"p0%d.pdf"%i, 'pdf Portrait')
    c_p1[i].SaveAs("SavedGraph/"+"p1%d.root"%i)
    c_p1[i].Print("SavedGraph/"+"p1%d.pdf"%i, 'pdf Portrait')
    c_p01[i].SaveAs("SavedGraph/"+"p0p1%d.root"%i)
    c_p01[i].Print("SavedGraph/"+"p0p1%d.pdf"%i, 'pdf Portrait')



    
