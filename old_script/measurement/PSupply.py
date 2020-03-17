#!/usr/bin/env python
#CH1 stage

import gpd3303s,time

gpd = gpd3303s.GPD4303S()
gpd.open('/dev/tty.usbserial-A4008T7f') #power supply

def PS_init(V1, V2, V3, V4): # V
##    gpd.enableOutput(0)
    time.sleep(1)
    gpd.setVoltage(1, V1)
    time.sleep(0.1)
    gpd.setVoltage(2, V2)
    time.sleep(0.1)
    gpd.setVoltage(3, V3)
    time.sleep(0.1)
    gpd.setVoltage(4, V4)
    time.sleep(0.1)

    gpd.enableOutput(1)
    time.sleep(2)
##    time.sleep(2.5)

    print('Ch 1: %.3f (V)' % gpd.getVoltageOutput(1))
    time.sleep(0.1)
    print('Ch 2: %.3f (V)' % gpd.getVoltageOutput(2))
    time.sleep(0.1)
    print('Ch 3: %.3f (V)' % gpd.getVoltageOutput(3))
    time.sleep(0.1)
    print('Ch 4: %.3f (V)' % gpd.getVoltageOutput(4))

PS_init(0,6,1.5,0)
# PS_init(24,0,0,0)
##for i in range(1000):
##    PS_init(24,0,0,0)
##    PS_init(0,0,0,0)
