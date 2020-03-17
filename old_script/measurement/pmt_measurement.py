#!/usr/bin/env python

#import ROOT
# import gpd3303s
import sigma_koki
import time
import numpy as np
import PSupply
import FGenerator
import readout
import OScope_tek as OScope
import PSoff

wavelength = 635
#initialization:
#def initialize(zeropos):
#  gsc02.returnToMechanicalOrigin(b'-', 0)
#  gsc02.move(zeropos * DEG2STEP)
#  gsc02.initializeOrigin(1,0)

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

#gpd = gpd3303s.GPD3303S()
#gpd.open('/dev/tty.usbserial-A600H0LE')

#Power
print("Power on:")
PSupply.PS_init(24.,6,1.5,0)
time.sleep(1)
#FG period(ns) width(ns) vlow(mV) vhigh(mV) delay(ns)

##FGenerator.initialize(wavelength)
time.sleep(1)

#OS
print("\nSetting up the oscilloscope:")
OScope.OS_init(0)


DEG2STEP = 400 # 400 steps of GSC02 is equal to 1 deg rotation
gsc02 = sigma_koki.GSC02()
gsc02.open('/dev/tty.usbserial-FTRTNEFZ')
status = gsc02.getStatus()
print('Initial stage status: ', status.decode())

# current_pos = int(status.split(b',')[0].replace(b' ', b''))
# if current_pos != 0:
#   #gsc02.returnToMechanicalOrigin('-', 0)
#   #gsc02.initializeOrigin(1,0)
#   gsc02.move(-current_pos, 0) # reset position
#   waitUntilRotationIsFinished(0)

#rotation cycle test
an_part0 = np.array([40,37])
an_part1 = np.arange(35,18,-1)
# an_part2 = np.arange(18,-3,-3)
an_part2 = np.arange(18,-21,-3)
an_part3 = np.arange(-19,-36,-1)
an_part4 = np.array([-37,-40])

angles = np.concatenate((an_part0, an_part1, an_part2, an_part3, an_part4))

# index = np.argwhere(angles == -15)
# index = index[0][0] + 1
# angles = np.arange(-24,41)
# angles = np.array([0])
#
print("\nSetting up the FG:")
FGenerator.initialize(wavelength)
#
for i in range(0,angles.size):
  print("\n\n\t=====Starting the cycle for angle: %d degrees fwd====="%angles[i])
  gsc02.setSpeed(1, 50, 1000, 1, 50, 1000, 1)
  time.sleep(1)
  gsc02.move(angles[i]*DEG2STEP, 0)
  waitUntilRotationIsFinished(angles[i]*DEG2STEP)
  status = gsc02.getStatus()
  current_pos = int(status.split(b',')[0].replace(b' ', b''))

##  gsc02.initializeOrigin(1,0) #imitate power off


  print("Stage power off")
  PSupply.PS_init(0.,6,1.5,0)

  time.sleep(1)
  print("Reading PMT")
  readout.readout(angles[i],50,"pmt/fwd")

  print("Stage power on")
  time.sleep(1)
  PSupply.PS_init(24.,6,1.5,0)
  time.sleep(1)
  gsc02.setSpeed(1, 50, 1000, 1, 50, 1000, 1)
  time.sleep(1)
  gsc02.move(-current_pos, 0)
  waitUntilRotationIsFinished(-current_pos)
  gsc02.initializeOrigin(1,0)
  print("waiting 3 seconds in 0deg, can interrupt now if needed")
  print(".........")
  time.sleep(1)
  print("......")
  time.sleep(1)
  print("...")
  time.sleep(1)
print("\nFWD done")

angles = angles * (-1)
index = np.argwhere(angles == -30)
index = index[0][0] + 1

for i in range(index, angles.size):
  print("\n\n\t=====Starting the cycle for angle: %d degrees bwd====="%angles[i])
  gsc02.setSpeed(1, 50, 1000, 1, 50, 1000, 1)
  time.sleep(1)
  gsc02.move(angles[i]*DEG2STEP, 0)
  waitUntilRotationIsFinished(angles[i]*DEG2STEP)
  status = gsc02.getStatus()
  current_pos = int(status.split(b',')[0].replace(b' ', b''))

##  gsc02.initializeOrigin(1,0) #imitate power off


  print("Stage power off")
  PSupply.PS_init(0.,6,1.5,0)
  time.sleep(1)
  print("Reading PMT")
  readout.readout(angles[i],50,"pmt/bwd")
  time.sleep(1)

  print("Stage power on")
  time.sleep(1)
  PSupply.PS_init(24.,6,1.5,0)
  time.sleep(1)
  gsc02.setSpeed(1, 50, 1000, 1, 50, 1000, 1)
  time.sleep(1)
  gsc02.move(-current_pos, 0)
  waitUntilRotationIsFinished(-current_pos)
  gsc02.initializeOrigin(1,0)
  print("waiting 3 seconds in 0deg, can interrupt now if needed")
  print(".........")
  time.sleep(1)
  print("......")
  time.sleep(1)
  print("...")
  time.sleep(1)
print("\nAll done")
PSoff.PS_off()

#plus = counter-clockwise
