import numpy as np
import ROOT


class Reader:
    def __init__(self, dataset, channel=1, onepecharge=0, extension=0):
        self.plambda = 0
        self.N = 0
        self.plambda_stat_error = 0
        self.plambda_sys_error = 0
        self.MeanOnePECharge = 0
        self.MeanOnePECharge_stat_error = 0
        self.dataset = str(dataset)
        self.channel = channel
        if onepecharge == 0:
            self.CalcMeanCharge()
            self.CalcLambda()
        else:
            self.SetMeanOnePE(onepecharge)
            # print("%s/hists/ch1_%d.root" % (self.dataset, voltage))
            if channel == 1:
                file = ROOT.TFile("%s/hists/ch1_%d.root" % (self.dataset, extension))
            elif channel == 2:
                file = ROOT.TFile("%s/hists/ch2_%d.root" % (self.dataset, extension))
            hist = file.Get('signal')
            hist1 = file.Get('noise')
            mean = hist.GetMean() - hist1.GetMean()
            error = np.sqrt(np.power(hist.GetMeanError(), 2) + np.power(hist1.GetMeanError(), 2))
            self.N = hist.GetEntries()
            file.Close()
            self.CalcLambda(mean, error)

    def CalcMeanCharge(self):
        file = ROOT.TFile("%s.root" % self.dataset)
        hOne = file.Get('hOneEst7')
        self.MeanOnePECharge = hOne.GetMean()
        self.MeanOnePECharge_stat_error = hOne.GetMeanError()  # to be changed later
        file.Close()

    def CalcLambda(self, mean=0, mean_error=0):
        if mean == 0:
            file = ROOT.TFile("%s.root" % self.dataset)
            hLit_aligned = file.Get('hLit_aligned')
            MeanCharge = hLit_aligned.GetMean()
            MeanCharge_error = hLit_aligned.GetMeanError()
            file.Close()
        else:
            MeanCharge = mean
            MeanCharge_error = mean_error
        self.plambda = MeanCharge / self.MeanOnePECharge
        self.plambda_stat_error = MeanCharge_error / MeanCharge
    def SetMeanOnePE(self, value):
        self.MeanOnePECharge = value
    def GetMeanOnePE(self):
        return self.MeanOnePECharge
    def GetLambda(self):
        return self.plambda
    def GetStatError(self):
        return self.plambda_stat_error
    def GetSysError(self):
        return self.plambda_sys_error
    def GetN(self):
        return self.N

# test = Reader('linearity_465_pmt/3500')
# print('lambda = %f +/- %f' % (test.GetLambda(), test.GetStatError()))
