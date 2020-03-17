import ROOT

wlen = 465

#experiment sipm
f_exp_sipm = ROOT.TFile("%d_response.root"%wlen)
can_exp_sipm = f_exp_sipm.Get("c1")
band_exp_sipm = can_exp_sipm.GetListOfPrimitives()[1]
graph_exp_sipm = can_exp_sipm.GetListOfPrimitives()[2]
normval_exp_sipm = graph_exp_sipm.GetY()[graph_exp_sipm.GetN()-1]

#experiment pmt
graph_exp_pmt = can_exp_sipm.GetListOfPrimitives()[3]
normval_exp_pmt = graph_exp_pmt.GetY()[graph_exp_pmt.GetN()-1]

#simulation sipm
f_sim_sipm = ROOT.TFile("%d_sim.root"%wlen)
can_sim_sipm = f_sim_sipm.Get("c1")
mg_sim_sipm = can_sim_sipm.GetPrimitive("")
graph_sim_sipm = mg_sim_sipm.GetListOfGraphs()[1]
normval_sim_sipm = graph_sim_sipm.GetY()[0]

coeff = normval_exp_sipm/normval_sim_sipm

for i in range(graph_sim_sipm.GetN()):
    graph_sim_sipm.GetY()[i] *= coeff
    
graph_sim_sipm.GetYaxis().SetRangeUser(-0.1, 3)
graph_sim_sipm.GetXaxis().SetRangeUser(-3., 42.)
graph_sim_sipm.SetTitle('%d nm;#theta angle, deg.; #lambda'%wlen)

#simulation pmt
graph_sim_pmt = mg_sim_sipm.GetListOfGraphs()[0]
normval_sim_pmt = graph_sim_pmt.GetY()[0]


for i in range(graph_sim_pmt.GetN()):
    graph_sim_pmt.GetY()[i] *= coeff


#drawing
c = ROOT.TCanvas()
c.SetGridx(1)
c.SetGridy(1)
graph_exp_sipm.SetLineColor(graph_sim_sipm.GetLineColor())
band_exp_sipm.SetFillColor(graph_sim_sipm.GetLineColor())
band_exp_sipm.SetFillStyle(3002)
graph_exp_pmt.SetLineColor(graph_sim_pmt.GetLineColor())

leg = ROOT.TLegend(0.70, 0.75, 0.9, 0.9)
leg.AddEntry(graph_sim_pmt, "PMT simulation", "l")
leg.AddEntry(graph_exp_pmt, "PMT experiment", "e")
leg.AddEntry(graph_sim_sipm, "SiPM simulation", "l")
leg.AddEntry(graph_exp_sipm, "SiPM expermiment", "e")


graph_sim_sipm.Draw("AL")
graph_exp_sipm.Draw("SAMEP")
band_exp_sipm.Draw("SAME3")
graph_exp_pmt.Draw("SAMEP")
graph_sim_pmt.Draw("SAMEL")
leg.Draw("SAME")
c.Update()
