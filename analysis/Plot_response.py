import ROOT
import numpy as np

import SiPMPE_reader
import PMTPE_reader

wavelength = 635

c1 = ROOT.TCanvas('c1', '-', 1000, 500)

angles = np.arange(-40, 41)

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

onepe = np.zeros(10)
onepe_mon = np.zeros(10)

# sipm = np.zeros(n)
# sipm_err = np.zeros(n)
# ratio = np.zeros(n)

onepe_f = ROOT.TFile("ch1_1pe_parts.root")
onepe_mon_f = ROOT.TFile("ch2_1pe_parts.root")

for i in range(10):
    onepe_h = onepe_f.Get("OnePE_%d" % (i + 1)).Clone()
    onepe_mon_h = onepe_mon_f.Get("OnePE_%d" % (i + 1)).Clone()
    onepe[i] = onepe_h.GetMean()
    onepe_mon[i] = onepe_mon_h.GetMean()
    
    del onepe_h
    del onepe_mon_h
    
onepe_f.Close()
onepe_mon_f.Close()

#meanOnepe = np.mean(onepe)
mean_1pe = np.mean(onepe)
#onepe_stat_err = np.std(onepe)
stat_err_1pe = np.std(onepe)
#meanOnepe_mon = np.mean(onepe_mon)
mean_1pe_mon = np.mean(onepe_mon)
#onepe_mon_stat_err = np.std(onepe_mon)
stat_err_1pe_mon = np.std(onepe_mon)

#onepe_rel_err = onepe_stat_err / meanOnepe
rel_err_1pe = stat_err_1pe / mean_1pe
#onepe_mon_rel_err = onepe_mon_stat_err / meanOnepe_mon
rel_err_1pe_mon = stat_err_1pe_mon / mean_1pe_mon

for i in range(n):
    pmt_data = PMTPE_reader.Reader('pmt/fwd/hists/ch1_%d.root' % angles[i], mean_1pe)
    pmt_monitor_data = PMTPE_reader.Reader('pmt/fwd/hists/ch2_%d.root' % angles[i], mean_1pe_mon)
    
    sipm_data = SiPMPE_reader.DistrReader("sipm_nocoating/hists/2500_0_4_%ddeg_fwd" % angles[i])
    sipm_monitor_data = PMTPE_reader.Reader('sipm_nocoating/monitor_fwd/hists/ch2_%d.root', mean_1pe_mon)
    
    pmt[i] = pmt_data.GetLambda()
    pmt_err[i] = pmt[i] * rel_err_1pe
    pmt[i] = pmt[i] / ROOT.TMath.Cos(angles[i]*ROOT.TMath.DegToRad())
    
    pmt_monitor[i] = pmt_monitor_data.GetLambda()
    pmt_monitor_err[i] = rel_err_1pe_mon
    
    sipm[i] = sipm_data.GetLambda() / ROOT.TMath.Cos(angles[i]*ROOT.TMath.DegToRad())
    sipm_err[i] = sipm_data.GetStatError()
    sipm_syserr[i] = sipm_data.GetSysError()
    sipm_monitor[i] = sipm_monitor_data.GetLambda()
    sipm_monitor_err[i] = sipm_monitor[i] * np.sqrt(np.power(sipm_monitor_data.GetStatError(), 2) + np.power(onepe_mon_rel_err, 2))

    ratio[i] = sipm[i] / pmt[i]
    print('(%d): lambda_sipm = %f\t lambda_pmt = %f\t ratio = %f'%(angles[i],sipm[i],pmt[i],ratio[i]))
    del pmt_data
    del sipm_data
    del pmt_monitor_data
    del sipm_monitor_data


mon_norm = np.mean(sipm_monitor) / np.mean(pmt_monitor)

for i in range(n):
    pmt[i] *= mon_norm
    
gr = ROOT.TGraphErrors(n, angles.astype(float), sipm,angles_err, sipm_err)
    
gr1 = ROOT.TGraphErrors(n, angles.astype(float), sipm, angles_err.astype(float), sipm_syserr)
gr2 = ROOT.TGraphErrors(n, angles.astype(float), pmt, angles_err.astype(float), pmt_err)
gr3 = ROOT.TGraphErrors(n, angles.astype(float), pmt_monitor, angles_err, pmt_monitor_err)
gr4 = ROOT.TGraphErrors(n, angles.astype(float), sipm_monitor, angles_err, sipm_monitor_err)

gr.SetLineColor(ROOT.kBlue)
gr4.SetLineColor(ROOT.kBlue)
gr2.SetLineColor(ROOT.kRed)
gr3.SetLineColor(ROOT.kRed)
gr1.SetFillColor(ROOT.kBlue);
gr1.SetFillStyle(3002);

gr1.SetTitle("%d nm;#theta angle, deg;#lambda" % wavelength)
gr1.GetXaxis().SetRangeUser(np.amin(angles.astype(float)) - 1., np.amax(angles.astype(float)) + 1.)
gr1.GetYaxis().SetRangeUser(0, np.amax(sipm) * 1.15)

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
