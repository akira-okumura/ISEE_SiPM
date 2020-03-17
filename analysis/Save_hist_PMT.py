import numpy as np
import sys
import math
from tqdm import tqdm

import ROOT

import PMT_reader

channel_monitor = 2
channel_main = 1

angles = np.arange(-40,41)

print("saving histograms for ch1")

for i in tqdm(range(len(angles))):
    pmt = PMT_reader.PMT('%d' % angles[i], channel_main, 'hists')
    pmt.Create_hist()
    del pmt
