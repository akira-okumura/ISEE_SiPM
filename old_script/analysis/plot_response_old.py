import ROOT
import numpy as np
import PEdistr
import PMT_reader
import SinglePE_reader

def CalcBinomialError(plambda, N):
    P0 = np.exp(-plambda)
    N0 = N * P0
    return (1. / N0) * np.sqrt(N * (1 - P0) * P0)

c1 = ROOT.TCanvas('c1','-',1000,500)
an_part0 = np.array([40,37])
an_part1 = np.arange(35,18,-1)
# an_part2 = np.arange(18,-3,-3)
an_part2 = np.arange(18,-21,-3)
an_part3 = np.arange(-19,-36,-1)
an_part4 = np.array([-37,-40])
angles = np.concatenate((an_part0, an_part1, an_part2, an_part3, an_part4))
##broken = np.array([-32, -36])
##l = len(broken)
##for i in range(0,l):
##    index = np.argwhere(angles == broken[i])
##    angles = np.delete(angles, index)
n = len(angles)
angles_err = np.full(n, 0.25)
pmt = np.zeros(n)
pmt_err = np.zeros(n)
pmt_monitor = np.zeros(n)
pmt_monitor_err = np.zeros(n)
sipm = np.zeros(n)
sipm_err = np.zeros(n)
sipm_syserr = np.zeros(n)
sipm_monitor = np.zeros(n)
sipm_monitor_err = np.zeros(n)
ratio = np.zeros(n)

onepe = np.zeros(8)
onepe_mon = np.zeros(8)
pmt_err = np.zeros(n)
# sipm = np.zeros(n)
# sipm_err = np.zeros(n)
# ratio = np.zeros(n)
voltage = np.arange(3300, 3500, 25)
for i in range(8):
    pmt_data = SinglePE_reader.Reader('pmt/single_pe/%d' % voltage[i])
    onepe[i] = pmt_data.GetMeanOnePE()
    del pmt_data
meanOnepe = np.mean(onepe)
onepe_stat_err = np.std(onepe)

for i in range(8):
    pmt_data = SinglePE_reader.Reader('pmt/single_pe/%d_monitor' % voltage[i])
    onepe_mon[i] = pmt_data.GetMeanOnePE()
    del pmt_data
meanOnepe_mon = np.mean(onepe)
onepe_mon_stat_err = np.std(onepe)



for i in range(0,n):
    pmt_data = SinglePE_reader.Reader('pmt/fwd' % angles[i], 1, meanOnepe, angles[i])
    pmt_monitor_data = SinglePE_reader.Reader('pmt/fwd' % angles[i], 2, meanOnepe_mon, angles[i])
    sipm_data = PEdistr.PEdistr("sipm/hists/3500_500_4_%ddeg_fwd"%angles[i])
    sipm_monitor_data = SinglePE_reader.Reader('sipm/monitor_fwd' % angles[i], 2, meanOnepe_mon, angles[i])
    pmt[i] = pmt_data.GetLambda()
    pmt_err[i] = CalcBinomialError(pmt[i], pmt_data.GetN())
    pmt[i] = pmt[i] / ROOT.TMath.Cos(angles[i]*ROOT.TMath.DegToRad())
    pmt_monitor[i] = pmt_monitor_data.GetLambda()
    pmt_monitor_err[i] = CalcBinomialError(pmt_monitor[i], pmt_monitor_data.GetN())
    sipm[i] = sipm_data.GetLambda() / ROOT.TMath.Cos(angles[i]*ROOT.TMath.DegToRad())
    sipm_err[i] = sipm_data.GetStatError()
    sipm_syserr[i] = sipm_data.GetSysError()
    sipm_monitor[i] = sipm_monitor_data.GetLambda()
    sipm_monitor_err[i] = CalcBinomialError(sipm_monitor[i], sipm_monitor_data.GetN())

    ratio[i] = sipm[i]/pmt[i]
    print('(%d): lambda_sipm = %f\t lambda_pmt = %f\t ratio = %f'%(angles[i],sipm[i],pmt[i],ratio[i]))
    del pmt_data
    del sipm_data
    del pmt_monitor_data
    del sipm_monitor_data

# pmt_add_fwd = np.zeros(n)
# pmt_add_fwd_err = np.zeros(n)
# for i in range(0,n):
#     pmt_data = PMT_fit.PMT('pmt_data_new','%ddeg_fwd'%angles[i], 1, 0)
#     pmt_add_fwd[i] = pmt_data.GetLambda() / ROOT.TMath.Cos(angles[i]*ROOT.TMath.DegToRad())
#     pmt_add_fwd_err[i] = pmt_data.GetError()
#     del pmt_data

# pmt_add_fwd = np.zeros(n)
# pmt_add_fwd_err = np.zeros(n)
# for i in range(0,n):
#     pmt_data = PMT_fit.PMT('pmt_data_new','%ddeg_fwd'%angles[i], 1, 0)
#     pmt_add_fwd[i] = pmt_data.GetLambda() / ROOT.TMath.Cos(angles[i]*ROOT.TMath.DegToRad())
#     pmt_add_fwd_err[i] = pmt_data.GetError()
#     del pmt_data

# angles_pmt = np.concatenate((angles, angles, angles))
# angles_pmt_err = np.full(3*n, 0.5)
# pmt_all = np.concatenate((pmt,pmt_add_fwd,pmt_add_fwd))
# pmt_all_err = np.concatenate((pmt_err,pmt_add_fwd_err,pmt_add_fwd_err))

for i in range(0,n):
   sipm[i] /= sipm_monitor[i]/pmt_monitor[0]
   pmt[i] /= pmt_monitor[i]/pmt_monitor[0]

gr = ROOT.TGraphErrors(n,angles.astype(float),sipm,angles_err,sipm_err)

gr1 = ROOT.TGraphErrors(n,angles.astype(float), sipm, angles_err.astype(float), sipm_syserr)
gr2 = ROOT.TGraphErrors(n,angles.astype(float), pmt, angles_err.astype(float), pmt_err)
gr3 = ROOT.TGraphErrors(n,angles.astype(float),pmt_monitor,angles_err,pmt_monitor_err)
gr4 = ROOT.TGraphErrors(n,angles.astype(float),sipm_monitor,angles_err,sipm_monitor_err)
gr.SetLineColor(ROOT.kBlue)
gr4.SetLineColor(ROOT.kBlue)
gr2.SetLineColor(ROOT.kRed)
gr3.SetLineColor(ROOT.kRed)
gr1.SetFillColor(ROOT.kBlue);
gr1.SetFillStyle(3002);

gr1.SetTitle("465 nm;#theta angle, deg;#lambda")
gr1.GetXaxis().SetRangeUser( np.amin(angles.astype(float)) - 1., np.amax(angles.astype(float)) + 1.)
gr1.GetYaxis().SetRangeUser(0, 1.9)
gr1.Draw("a3")
gr.Draw("SAMEP")
gr2.Draw("SAMEP")
gr3.Draw("SAMEP")
gr4.Draw("SAMEP")

leg = ROOT.TLegend(0.80, 0.75, 0.9, 0.9)
leg.AddEntry(gr, "sipm", "e")
leg.AddEntry(gr2, "pmt", "e")
leg.Draw()
c1.SetGridy(1)

c1.Update()
