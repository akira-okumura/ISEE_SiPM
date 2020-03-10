import time
import AFG_TEKTRONIX

"""
Pulse_Geneartor Setting script

import FG_control
FG = FG_control.FG()
FG_setinit.monitor(wl)

witten by YK
"""

class FG(object):
    def __init__(self):
        self.tek = AFG_TEKTRONIX.AFG3251()
        self.tek.open('USB0::0x0699::0x0344::C020398::INSTR')
                
    def monitor(self, wl): 
        #must be changed
        period, width, vlow, vhigh, delay = self.initialize_A(wl) #ns ns mV mV ns
        
        print("turning output off")
        self.tek.setOutputOFF()
        
        self.tek.setFunction("PULS")
        print("Function = " + self.tek.getFunction())
        
        self.tek.setPulsePeriod(period)
        print("Period = " + self.tek.getPulsePeriod() + " ns")
        
        self.tek.setPulseWidth(width)
        print("Width = " + self.tek.getPulseWidth() + " V")
        
        self.tek.setV_High(vhigh)
        print("Voltage High = " + self.tek.getV_High() + " V")
        
        self.tek.setV_Low(vlow)
        print("Voltage Low = "+ self.tek.getV_Low() + " V")
        
        self.tek.setPulseDelay(delay)
        print("Delay = " + self.tek.getPulseDelay() + " V")
        
        print("set Continuous mode")
        self.tek.setContinuousMode()
        
        print("turning output on")
        self.tek.setOutputON()
        
        print("The FG is ready")
        
    def target(self, wl):
        #must be changed
        period, width, vlow, vhigh, delay = self.initialize_A(wl) #ns ns mV mV ns
        
        print("turning output off")
        self.tek.setOutputOFF()
        
        self.tek.setFunction("PULS")
        print("Function = " + self.tek.getFunction())
        
        #self.tek.setPulsePeriod()
        #print("Period = " + self.tek.getPulsePeriod() + " ns")
        
        self.tek.setPulseWidth(width)
        print("Width = " + self.tek.getPulseWidth() + " V")
        
        self.tek.setV_High(vhigh)
        print("Voltage High = " + self.tek.getV_High() + " V")
        
        self.tek.setV_Low(vlow)
        print("Voltage Low = "+ self.tek.getV_Low() + " V")
        
        self.tek.setPulseDelay(delay)
        print("Delay = " + self.tek.getPulseDelay() + " V")
        
        self.tek.setTriggerdMode()
        print("TriggerdMode = " + self.tek.getBurstMode())
        
        self.tek.setBurstNcycles(1)
        print("BurstNcycles = " + self.tek.getBurstNcycles())
        
        self.tek.setTriggerExternal()
        print("TriggerSource = " + self.tek.getTriggerSource())
        
        print("turning output on")
        self.tek.setOutputON()
        
        print("The FG is ready")

    def target_V(self, width, vhigh, vlow, delay):
        #must be changed
        period = 500
        #delay = 0
        
        print("turning output off")
        self.tek.setOutputOFF()
        
        self.tek.setFunction("PULS")
        print("Function = " + self.tek.getFunction())
        
        #self.tek.setPulsePeriod()
        #print("Period = " + self.tek.getPulsePeriod() + " ns")
        
        self.tek.setPulseWidth(width)
        print("Width = " + self.tek.getPulseWidth() + " V")
        
        self.tek.setV_High(vhigh)
        print("Voltage High = " + self.tek.getV_High() + " V")
        
        self.tek.setV_Low(vlow)
        print("Voltage Low = "+ self.tek.getV_Low() + " V")
        
        self.tek.setPulseDelay(delay)
        print("Delay = " + self.tek.getPulseDelay() + " V")
        
        self.tek.setTriggerdMode()
        print("TriggerdMode = " + self.tek.getBurstMode())
        
        self.tek.setBurstNcycles(1)
        print("BurstNcycles = " + self.tek.getBurstNcycles())
        
        self.tek.setTriggerExternal()
        print("TriggerSource = " + self.tek.getTriggerSource())
        
        print("turning output on")
        self.tek.setOutputON()
        
        print("The FG is ready")

        
    def setOutputOFF(self):
        self.tek.setOutputOFF()
                    
    def initialize_A(self, wl):
        """
        Anatolii's setting
        """
        if wl==465:
            return 500, 4, 500, 3500, 0
        elif wl==375:
            return 500, 4, 1000, 3800, 0
        elif wl==310:
            return 500, 10, 0, 4400, 0
        elif wl==558:
            return 500, 4, 700, 3300, 0
        elif wl==402:
            return 500, 5, 1050, 3600, 0
        elif wl==635:
            return 500, 4, 0, 2500, 0
        else:
            raise ValueError('LED wavelength is not match')
            
    def close(self):
        self.tek.close()

if __name__ == '__main__':
    
    ##################################################
    fg = FG()
    fg.monitor(465)
    time.sleep(1)

    fg.setOutputOFF()
    fg.close()
    ##################################################
