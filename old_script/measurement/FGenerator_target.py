#!/usr/bin/env python

import visa, time

def FG_init(width, vlow, vhigh, delay): #ns mV mV ns
    rm = visa.ResourceManager()
    try:
        tek = rm.open_resource('USB0::0x0699::0x0344::C020398::INSTR')
    except visa.VisaIOError:
        tek = rm.open_resource('USB0::0x0699::0x0344::C020398::INSTR')
    time.sleep(0.5)
    print("turning output off")
    print(tek.write('OUTP 0'))
    time.sleep(0.5)
    print("setting PULSe")
    print(tek.write("SOURce:FUNCtion PULSe"))
    time.sleep(0.5)
    print(tek.query("SOURce:FUNCtion?"))
    time.sleep(0.5)
    print(tek.write("SOURce:BURSt:STAT 1"))
    time.sleep(0.5)
    print(tek.write("SOURce:BURSt:MODE TRIGgered"))
    time.sleep(0.5)
    print(tek.query("SOURce:BURSt:MODE?"))
    time.sleep(0.5)
    print(tek.write("SOURce:BURSt:NCYC 1"))
    time.sleep(0.5)
    print(tek.query("SOURce:BURSt:NCYC?"))
    time.sleep(0.5)


    print("setting WIDT")
    print(tek.write('SOURce:PULSe:WIDT %dns'%width))
    time.sleep(0.5)
    print(tek.query("SOURce:PULSe:WIDT?"))
    time.sleep(0.5)

    print("setting HIGH")
    print(tek.write('SOURce:VOLT:HIGH %dmV'%vhigh))
    time.sleep(0.5)
    print(tek.query("SOURce:VOLT:HIGH?"))
    time.sleep(0.5)
##    print("setting HIGH")
##    print(tek.write('SOURce:VOLT:LIM:LOW %dmV'%vlow))
##    time.sleep(0.5)
    print("setting LOW")
    print(tek.write('SOURce:VOLT:LOW %dmV'%vlow))
    time.sleep(0.5)
    print(tek.query("SOURce:VOLT:LOW?"))
    time.sleep(0.5)

##    print("setting PER")
##    print(tek.write('SOURce:PULSe:PER 1000ns'))
##    time.sleep(0.5)
##    print(tek.query("SOURce:PULSe:PER?"))
##    time.sleep(0.5)

    print("setting TRIG")
    print(tek.write('TRIGger:SOURce EXTernal'))
    time.sleep(0.5)
    print(tek.write('TRIGger:SOURce?'))
    time.sleep(0.5)

    print("setting DEL")
    print(tek.write('SOURce:PULSe:DEL %dns'%delay))
    time.sleep(0.5)
    print(tek.query("SOURce:PULSe:DEL?"))
    time.sleep(0.5)

    print("turning output on")
    print(tek.write('OUTP 1'))
    time.sleep(0.5)
    print("The FG is ready")
    tek.clear()
    tek.close()

def initialize(wl):
    if wl==465:
        FG_init(4, 500, 3500, 0)
    elif wl==375:
        FG_init(4, 1000, 3800,0)
    elif wl==310:
        FG_init(10, 0, 4400, 0)
    elif wl==558:
        FG_init(4, 700, 3300, 0)
    elif wl==402:
        FG_init(5, 1050, 3600, 0)
    elif wl==635:
        FG_init(4, 0, 2500, 0)

# initialize(635)
