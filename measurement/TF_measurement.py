#!/usr/bin/env python

import time
import datetime

import Takedata_TARGET
import PowerSupply_control
import TC_08_2

print("Power on")
ps = PowerSupply_control.PS()
ps.Open()
ps.Init_TARGET()
ps.OutputON_Stage()

time.sleep(100)

Temp_file = open("/Volumes/Untitled/kuroda/2020target/run/202003run_Delay352/Temp.dat", "w")

target_runid = 0
Takedata_TARGET.Takedata("/Volumes/Untitled/kuroda/2020target/run/202003run_Delay352/dummy.fits", 200, target_runid, 0)

target_runid = 1
for i in range(0, 4096, 1):
  Takedata_TARGET.Takedata("/Volumes/Untitled/kuroda/2020target/run/202003run_Delay352/TF_acq_%d.fits" % (i), 200, target_runid, i)


  time.sleep(0.5)
  
  temp = TC_08_2.GetTemp()
  dt_now = datetime.datetime.now()
  print("{} {} {} {} {} {} {} {} {}".format(dt_now, temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7]), file = Temp_file)
  
Temp_file.close()
  
print("Power off")
ps.OutputOFF()
ps.Close()
