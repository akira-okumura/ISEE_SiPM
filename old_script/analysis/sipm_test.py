import numpy as np
from tqdm import tqdm
import SiPM_reader
import sys
import argparse

args = sys.argv
instance = int(args[1])

an_part0 = np.array([40,37])
an_part1 = np.arange(35,18,-1)
# an_part2 = np.arange(18,-3,-3)
an_part2 = np.arange(18,-21,-3)
an_part3 = np.arange(-19,-36,-1)
an_part4 = np.array([-37,-40])

angles = np.concatenate((an_part0, an_part1, an_part2, an_part3, an_part4))

# index = np.argwhere(angles == 28)
# index = index[0][0]

# sipm = SiPM_reader.SiPM('2500_0_4_0deg_fwd.fits', 0, 8, 1)
# sipm.makehist()

for k in tqdm(range(len(angles))):
#
    for i in tqdm(range(4)):
        print('======= start: %d deg ========' % angles[k])
        if instance == 0:
            for j in tqdm(range(0, 16, 2)):
                sipm = SiPM_reader.SiPM('2500_0_4_%ddeg_fwd.fits' % angles[k], i, j, 1)
                sipm.makehist()
        elif instance == 1:
            for j in tqdm(range(1, 16, 2)):
                sipm = SiPM_reader.SiPM('2500_0_4_%ddeg_fwd.fits' % angles[k], i, j, 1)
                sipm.makehist()
#
# angles = angles * (-1)
#
# for k in tqdm(range(len(angles))):
#     for i in tqdm(range(4)):
#         print(angles[k])
#         if instance == 0:
#             for j in tqdm(range(0, 16, 2)):
#                 sipm = SiPM_reader.SiPM('4400_1150_4_%ddeg_bwd.fits' % angles[k], i, j, 1)
#                 sipm.makehist()
#         elif instance == 1:
#             for j in tqdm(range(1, 16, 2)):
#                 sipm = SiPM_reader.SiPM('4400_1150_4_%ddeg_bwd.fits' % angles[k], i, j, 1)
#                 sipm.makehist()
