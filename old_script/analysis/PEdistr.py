import target_driver
import target_io
import argparse
import numpy as np
import math
import ROOT
import sys
import SiPM_reader


class PEdistr:
    def __init__(self, dataset):
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
                sipm = SiPM_reader.SiPM(self.dataset, asic, channel, 0)
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
                hist_s.Delete()
                hist_n.Delete()
                del sipm
        self.stat_error = np.sqrt(self.GetStatError())
        self.sys_error = np.sqrt(self.GetSysError())

    def GetLambdaHist(self):
        return self.hist
    def GetLambdaDistr(self):
        return self.distr

# #
# PEd = PEdistr('/Volumes/Untitled/zenin/linearity_465/linearity_465_sipm/hists/3500_4_465')
#
# total = PEd.GetLambda()
# stat_err = PEd.GetStatError()
# sys_err = PEd.GetSysError()
#
# print('total lambda = %f \u00B1 %f stat \u00B1 %f sys'%(total, stat_err, sys_err))
# print('relative uncertainty = %f%% stat + %f%% sys'%(stat_err/total*100, sys_err/total*100))
#
# h = PEd.GetLambdaDistr().Clone()
# print(h.GetBinContent(9))
# h.Draw()
