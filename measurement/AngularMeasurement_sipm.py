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
angles = np.arange(-40,41)

#PMT Setting up


for i in range(len(angles)):
    print("\n\n\t=====Starting the cycle for angle: %d degrees =====" % angles[i])
    if target_runid == 0:
        print("Waiting 3 seconds in 0deg, can interrupt now if needed")
        print(".........")
        time.sleep(1)
        print("......")
        time.sleep(1)
        print("...")
        time.sleep(1)

    stage.rotation(angles[i], 50)
    
    current_pos = stage.GetAngle()
    
    print("Setting up the FG:Monitor")
    fg.monitor(wavelength)
    time.sleep(1)

     
    print("Reading PMT")
    Oscillo_read.Get_12_waveform("test/test/" + str(angles[i]), 50)
    time.sleep(1)
    
    print("Setting up the KEYTHLEY:TARGET")
    keithley.HighVol_init()
    time.sleep(3)
    keithley.ILimitSet(10 * 10 **(-3))
    keithley.HighVolON(60)
    print("KEITHLEY V = " + str(keithley.HighVolGetV()) + " V")
    print("KEITHLEY I = " + str(keithley.HighVolGetA()) + " A")
    time.sleep(10)

    print("Setting up the FG:TARGET")
    fg.target(wavelength)
    time.sleep(1)

    print("Reading SiPM")
    Takedata_TARGET.Takedata("test/test/3500_500_4_%ddeg_fwd.fits" % (angles[i]), 40000, target_runid, 900)

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
