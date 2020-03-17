import visa, time

class KEITHLEY2450(object):
    def open(self, USBID):
        self.rm = visa.ResourceManager()
        self.keithley = self.rm.open_resource(USBID)
        time.sleep(0.1)

    def close(self):
        self.keithley.close()

    def write(self, command):
        self.keithley.write(command)
        time.sleep(0.5)

    def read(self):
        return self.keithley.read()

    def HighVolON(self, Voltage, Vstep = 10):
        self.write(':SOUR:VOLT:LEV 0\n')
        self.write(':OUTP ON\n')
        V = 0
        for i in range(int(Voltage / Vstep)) :
            V = Vstep * (i + 1)
            atemp = ':SOUR:VOLT:LEV %d\n' % V
            self.write(atemp)	

        for i in range(int(Voltage - V)) :
            Vi = V + (i + 1)
            atemp = ':SOUR:VOLT:LEV %d\n' % Vi
            self.write(atemp)	

        atemp = ':SOUR:VOLT:LEV %f\n' % Voltage
        self.write(atemp)
        

        for i in range(3):
            self.write('read?\n')           # get act. Current
            a = self.read()	

    def HighVolOFF(self, Vstep = 10):
        self.write(':SOUR:VOLT:LEV?\n') # get Voltage Setting
        Vol = self.read()
        Voltage = float(Vol[:-1])
        
        for i in range(int(Voltage / Vstep)) :
            V = Voltage - Vstep * (i + 1)
            atemp = ':SOUR:VOLT:LEV %d\n'%V
            self.write(atemp)
            
        self.write(':SOUR:VOLT:LEV 0\n')
        self.write(':OUTP OFF\n')	

        for i in range(3):
            self.write('read?\n')           # get act. Current
            a = self.read()

    def ILimitSet(self, Ilimit):
        command = ':SOUR:VOLT:ILIM %f\n' % Ilimit
        self.write(command)

    def HighVolGetV(self):
        self.write(':SOUR:VOLT:LEV?\n') # get Voltage Setting
        a = self.read()
        return float(a[:-1])  

    def HighVolGetA(self):
        self.write('read?\n')           # get act. Current
        a = self.read()
        return float(a[:-1])  

    def HighVol_init(self):
        wait_sec = 0.05
        self.write('*RST\n')
        self.write(':SENS:FUNC "CURR"\n')
        self.write(':SOUR:FUNC VOLT\n')
        self.write(':SOUR:VOLT:RANG 200\n')
        # current
        self.write(':SENS:CURR:RANG:AUTO ON\n')
        self.write(':SOUR:VOLT:ILIM 500E-6\n')  #Change Code for 2450 (CurrLimit500uA)
        #self.write(':FORM:ELEM CURR\n')        #Delete Code for 2450
        self.write(':SOUR:VOLT:LEV 0\n')
        #self.write(':OUTP ON\n')

keithley = KEITHLEY2450()
keithley.open('USB0::0x05E6::0x2450::04416732::INSTR')
        
if __name__ == '__main__':
    # high voltage


    keithley.HighVol_init()
    time.sleep(1)
    keithley.ILimitSet(10 * 10 **(-3))
    keithley.HighVolON(60)
    print(keithley.HighVolGetA())
    print(keithley.HighVolGetV())
    keithley.HighVolOFF()
    keithley.close()
