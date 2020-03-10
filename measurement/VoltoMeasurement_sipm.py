import time
import numpy as np

import Takedata_TARGET
import Oscillo_read
import PowerSupply_control
import FG_control
import Stage_control
import KEITHLEY

wavelength = 635
target_runid = 0

#Function Generator
fg = FG_control.FG()

#Power Supply
print("Power on")
ps = PowerSupply_control.PS()
ps.Open()
ps.Init_Stage()
ps.Init_TARGET()
ps.OutputON_Stage()

time.sleep(100)

#Stage
stage = Stage_control.Stage()
stage.Open()

print('Initial Rotation stage status: ', stage.GetX(), stage.GetZ())
print('Initial XZ stage status: ', stage.GetAngle())

#KEITHLEY
keithley = KEITHLEY.keithley

#rotation angle
#angles = np.arange(-40,41)
angle = 0

#PMT Setting up

vhighs = [0, 10, 20, 2000, 2500, 3000, 3500, 4000]
#vhighs = [0, 0, 0, 0, 0]


measurement = 0
for i in range(len(vhighs)):

    print("\n\n\t=====Starting the cycle for angle: %d degrees =====" % angle)
    if target_runid == 0:
        print("Waiting 3 seconds in 0deg, can interrupt now if needed")
        print(".........")
        time.sleep(1)
        print("......")
        time.sleep(1)
        print("...")
        time.sleep(1)

    #stage.rotation(angle, 50)
    
    current_pos = stage.GetAngle()
    
    print("Setting up the FG:Monitor")
    fg.monitor(wavelength)
    time.sleep(1)

    print("Reading PMT")
    #Oscillo_read.Get_12_waveform("test/test/" + str(angles[i]), 50)
    time.sleep(1)
    
    print("Setting up the KEYTHLEY:TARGET")
    keithley.HighVol_init()
    time.sleep(3)
    keithley.ILimitSet(30 * 10 **(-3))
    keithley.HighVolON(60)
    print("KEITHLEY V = " + str(keithley.HighVolGetV()) + " V")
    print("KEITHLEY I = " + str(keithley.HighVolGetA()) + " A")
    time.sleep(10)

    print("Setting up the FG:TARGET")
    fg.target_V(4, vhighs[i], 0, 0)
    time.sleep(1)

    print("Reading SiPM")
    Takedata_TARGET.Takedata("test/data0310_2/V%d_0_%dnm_NFCOFF.fits" % (vhighs[i], wavelength), 1000, target_runid, 900)
    #Takedata_TARGET.Takedata("test/data0305/V%d_0_%dnm_try%dTriggerDelay320.fits" % (vhighs[i], wavelength, measurement), 1000, target_runid, 900)
    measurement += 1

    target_runid = 1

    print("Finished Reading")

    print("KEYTHLEY power off")
    keithley.HighVolOFF()
    
    time.sleep(1)

ps.OutputOFF()
ps.Close()

fg.setOutputOFF()
fg.close()


Oscillo_read.close()

keithley.close()
