import visa, time

"""
Read AFG3000 Series Arbitrary Function Generators Programmer Manual
written by YK
"""
class AFG3251(object):
    """
    Tektronix AFG3251 pulse generator
    """
    def open(self, USBID):
        self.rm = visa.ResourceManager()
        self.afg = self.rm.open_resource(USBID)
        time.sleep(0.1)

    def close(self):
        self.afg.close()

    def write(self, command):
        self.afg.write(command)
        time.sleep(0.1)
        
    def query(self, command):
        temp = self.afg.query(command)[:-1]
        time.sleep(0.1)
        return temp

    def setOutputON(self):
        self.write('OUTPut:STATe ON')

    def setOutputOFF(self):
        self.write('OUTPut:STATe OFF')

    def setTriggerdMode(self):
        self.write('SOURce:BURSt:STAT ON')
        self.write('SOURce:BURSt:MODE TRIGgered')

    def setContinuousMode(self):
        self.write('SOURce:BURSt:STAT OFF')

    def getBurstMode(self):
        return self.query('SOURce:BURSt:MODE?')

    def setBurstDelay(self, delay):
        command = 'BURSt:TDELay %dns' % delay #Set BURST Trigger delay = 0.0
        self.write(command)
        
    def setBurstNcycles(self, N):
        command = 'SOURce:BURSt:NCYCles %d' % N
        self.write(command)
        
    def getBurstNcycles(self):
        return self.query('SOURce:BURSt:NCYCles?')

    def setFunction(self, shape):
        """
        SINusoid, SQUare, PULSe, RAMP, PRNoise, DC, SINC, GAUSsian, LORentz, ERISe, EDECay
        """
        command = 'SOURce:FUNCtion ' + shape
        self.write(command)
        
    def getFunction(self):
        return self.query('SOURce:FUNCtion?')

    def setPulseDelay(self, delay):
        command = 'SOURce:PULSe:DELay %dns' % delay
        self.write(command)
        
    def getPulseDelay(self):
        return self.query('SOURce:PULSe:DELay?')

    def setPulsePeriod(self, period):
        command = 'SOURce:PULSe:PER %dns' % period
        self.write(command)
        
    def getPulsePeriod(self):
        return self.query('SOURce:PULSe:PER?')

    def setPulseWidth(self, width):
        command = 'SOURce:PULSe:WIDTh %dns' % width
        self.write(command)
        
    def getPulseWidth(self):
        return self.query('SOURce:PULSe:WIDTh?')

    def setV_High(self, vhigh):
        command = 'SOURce:VOLTage:HIGH %dmV' % vhigh
        self.write(command)
        
    def getV_High(self):
        return self.query('SOURce:VOLTage:HIGH?')
         

    def setV_Low(self, vlow):
        command = 'SOURce:VOLTage:LOW %dmV' % vlow
        self.write(command)
        
    def getV_Low(self):
        return self.query('SOURce:VOLTage:LOW?')
    
    def setTriggerExternal(self):
        self.write('TRIGger:SOURce EXTernal')

    def getTriggerSource(self):
        return self.query('TRIGger:SOURce?')
