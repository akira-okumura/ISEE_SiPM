import numpy as np
import ROOT


class Reader:
    def __init__(self, dataset, onepecharge = 0):
        self.plambda = 0
        self.N = 0
        self.plambda_stat_error = 0
        self.plambda_sys_error = 0
        self.MeanOnePECharge = 0
        self.MeanOnePECharge_stat_error = 0
        self.dataset = str(dataset)
        
        if onepecharge == 0:
            self.CalcMeanCharge()
            self.CalcLambda()
        else:
            self.SetMeanOnePE(onepecharge)

            file = ROOT.TFile("%s" % self.dataset)
            
            hist_signal = file.Get('signal')
            hist_noise = file.Get('noise')
            mean = hist_signal.GetMean() - hist_noise.GetMean()
            error = np.sqrt(np.power(hist_signal.GetMeanError(), 2) + np.power(hist_noise.GetMeanError(), 2))
            self.N = hist_signal.GetEntries()            
            
            file.Close()
            self.CalcLambda(mean, error)

    def CalcMeanCharge(self):
        file = ROOT.TFile("%s" % self.dataset)
        hOne = file.Get('hOneEst7')
        self.MeanOnePECharge = hOne.GetMean()
        self.MeanOnePECharge_stat_error = hOne.GetMeanError()  # to be changed later
        
        file.Close()

    def CalcLambda(self, mean = 0, mean_error = 0):
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
