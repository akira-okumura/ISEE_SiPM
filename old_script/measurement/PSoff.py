#!/usr/bin/env python

import gpd3303s,time

gpd = gpd3303s.GPD4303S()
gpd.open('/dev/tty.usbserial-A4008T7f')

def PS_off():

    gpd.enableOutput(0)
    time.sleep(2)

    print('Ch 1: %.3f (V)' % gpd.getVoltageOutput(1))
    print('Ch 2: %.3f (V)' % gpd.getVoltageOutput(2))
    print('Ch 3: %.3f (V)' % gpd.getVoltageOutput(3))
    print('Ch 4: %.3f (V)' % gpd.getVoltageOutput(4))

##time.sleep(3600*2)
# PS_off()
