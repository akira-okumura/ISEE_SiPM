import numpy as np
from tqdm import tqdm
import SiPM_reader
import sys

angles = np.arange(-40, 41)

# sipm = SiPM_reader.SiPM('2500_0_4_0deg_fwd.fits', 0, 8, 1)
# sipm.makehist()

vhigh = 2500 #mV
vlow = 0 #mV
width = 4 #ns

for k in tqdm(range(len(angles))):
    for i in tqdm(range(4)):
        print('======= start: %d deg ========' % angles[k])
        for j in tqdm(range(16)):
            sipm = SiPM_reader.SiPM('%d_%d_%d_%ddeg_fwd.fits' % (vhigh, vlow, width, angles[k]), i, j)
            sipm.makehist()

