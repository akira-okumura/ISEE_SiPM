#!/usr/bin/env python

import visa, time

def OS_init(mode):
    rm = visa.ResourceManager()

    # open oscilloscope
    # USB
##    mso = rm.open_resource('USB0::0x0699::0x041B::C022756::INSTR')
    # TCPIP
    mso = rm.open_resource('TCPIP0::192.168.1.1::inst0::INSTR')

    time.sleep(0.1)
    print("Setting trigger")
    mso.write("TRIGger:A:TYPe EDGe") #set trig type
    time.sleep(0.3)
    mso.write("TRIGger:A:EDGE:COUPling AC")
    time.sleep(0.3)
    mso.write("TRIGger:A:EDGE:SLOpe RISe")
    time.sleep(0.3)
    # mso.write("TRIGger:A:EDGE:SOUrce AUXin")
    # time.sleep(0.3)
    # mso.write("TRIGger:A:LEVel:AUXin 890") #set trig to 1.2V
    # time.sleep(0.3)
    print("Setting channels")
    mso.write("CH1:SCAle 10E-3") #set channel gain
    time.sleep(0.3)
    mso.write("CH2:SCAle 5E-3") #set channel gain
    time.sleep(0.3)
    print("Setting scale and sample number")
    mso.write("HORizontal:SCAle 40E-9") #set time scale
    time.sleep(0.3)
    mso.write("HORizontal:SAMLERate 2.5E+9") #set time scale
    time.sleep(0.3)
    print("Setting waveform length")
    # mso.write("WFMInpre:NR_Pt 1E+5")
    # print(mso.query("WFMInpre:NR_Pt?"))
    # time.sleep(0.3)
    npoints = 1000000
    # print(npoints)
    # print(mso.query("WFMOutpre:NR_Pt?"))
    # time.sleep(0.3)

    if mode == 0: # for PMT
        mso.write("DATa:STARt 1")
        time.sleep(0.3)
        mso.write("DATa:STOP %d" % npoints)
        print('PMT acquisition')
        print(mso.query("DATa:STOP?"))
    elif mode == 1: # for TARGET
        mso.write("DATa:STARt %d" % (int(npoints/2) - 1000))
        time.sleep(0.3)
        mso.write("DATa:STOP %d" % (int(npoints/2) + 1000))
        print('TARGET acquisition')
        print(mso.query("DATa:STOP?"))
    print("The oscilloscope is ready")




# OS_init(1)
