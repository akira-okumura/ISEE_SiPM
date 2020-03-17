#!/usr/bin/env python

#import ROOT
import sigma_koki
import time
import numpy as np
import PSupply
import PSoff

def waitUntilRotationIsFinished(goal):
  for i in range(10000):
      time.sleep(0.01)
      status = gsc02.getStatus()
      current_pos = int(status.split(b',')[0].replace(b' ', b''))
      flag1, flag2, flag3 = status.split(b',')[2:5]
      if current_pos == goal and flag1 == b'K' and flag2 == b'K' and flag3 == b'R':
          print('\nRotation complete')
          return
      elif flag1 == b'K' and flag2 == b'K' and flag3 == b'B':
          print('\nCurrent Position: %7.2f deg (%s)' % (float(current_pos)/DEG2STEP, status.decode()), end='')
      else:
          print('Error: ', status.decode())

#Power

#FG period(ns) width(ns) vlow(mV) vhigh(mV) delay(ns)


PSoff.PS_off()

DEG2STEP = 400 # 400 steps of GSC02 is equal to 1 deg rotation
gsc02 = sigma_koki.GSC02()
gsc02.open('/dev/tty.usbserial-FTRTNEFZ')
status = gsc02.getStatus()
print('Initial stage status: ', status.decode())
# gsc02.returnToMechanicalOrigin(b'-',b'-')

an_part0 = np.array([40,37])
an_part1 = np.arange(35,18,-1)
# an_part2 = np.arange(18,-3,-3)
an_part2 = np.arange(18,-21,-3)
an_part3 = np.arange(-19,-36,-1)
an_part4 = np.array([-37,-40])

angles = np.concatenate((an_part0, an_part1, an_part2, an_part3, an_part4))
print("Power on:")
PSupply.PS_init(24.,0,0,0)
time.sleep(1)
for i in range(len(angles)):
    print(angles[i])
    gsc02.setSpeed(1, 50, 1000, 1, 50, 1000, 1)
    gsc02.move(angles[i] * DEG2STEP, 0)
    waitUntilRotationIsFinished(angles[i] * DEG2STEP)
    time.sleep(1)
    print("Power off:")
    PSupply.PS_init(0.,0,0,0)
    time.sleep(1)
    print("Power on:")
    PSupply.PS_init(24.,0,0,0)
    time.sleep(1)
    gsc02.setSpeed(1, 50, 1000, 1, 50, 1000, 1)
    gsc02.move(-angles[i] * DEG2STEP, 0)
    waitUntilRotationIsFinished(-angles[i] * DEG2STEP)
    time.sleep(1)
    gsc02.initializeOrigin(1,0)
    time.sleep(1)




print("\nAll done")
PSoff.PS_off()

#plus = counter-clockwise
