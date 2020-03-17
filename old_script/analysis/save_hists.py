import numpy as np
# import isee_sipm
import math
import ROOT
import sys
import PMT_reader
from tqdm import tqdm

args = sys.argv
channel = int(args[1])

print("saving histograms for ch%d"%channel)
for i in tqdm(range(3300, 3700, 25)):
    pmt = PMT_reader.PMT('%d' % i, channel, 1, 'hists')
    pmt.SaveHist()
    del pmt
