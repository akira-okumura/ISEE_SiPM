import visa,time,gzip,os

##################################################################
# to Control the oscilloscope MSO4054B Tektronix
#
# import Oscillo_read
#
# (1) Save waveform data from directed CH (only a CH )
#
#   Oscillo_read.Get_waveform(str FileName, Times of measurement , measured CH)
#
#    ex)  Oscillo_read.Get_waveform("pmt/nonfilter/10deg", 50 , 1)  
#             "times=50" == 40000 events, 
#             2.5GS/s , 0.4ns/points x 1Mpoints = 400us/1measured
#             LED 2MHz, 500ns/1flashEvent ,   400us/500ns = 800events/measuredTimes
#             800 x 50times = 40000 events
#
# (2) Save waveform data from CH1 and CH2
#
#   Oscillo_read.Get_12_waveform(str FileName, Times of measurement)
#
#    ex)  Oscillo_read.Get_12_waveform("pmt/filtered/10deg", 50)  
#
##################################################################

class MSO4054B(object):
    """
    Tektronix MSO4054B Oscilloscope
    """
    def open(self, port):
        self.rm = visa.ResourceManager()
        self.mso = self.rm.open_resource(port)

        ## visa with USB
        #self.mso = self.rm.open_resource('USB0::0x0699::0x040a::C010237::INSTR')
        
        ## visa with TCPIP
        #self.mso = self.rm.open_resource('TCPIP0::192.168.1.1::inst0::INSTR')
        time.sleep(3)
        
    def write(self, command):
        self.mso.write(command)
        time.sleep(0.1)

    def read(self):
        return self.mso.read_raw()

    def close(self):
        self.mso.close()

def savewaveform(file,CH):

    osc.write("DATa:SOUrce CH%s"%str(CH))    

    delim = b"***"
    osc.write("WAVFrm?")
    data = osc.read()
    time.sleep(0.1)

    if data[-1] == b'\n':
        waveform = data[:-1]
    else:
        waveform = data

    file.write(waveform + delim)
    wavefom = None
    del(waveform)

def Get_12_waveform(fname, Nevents): #in seconds

    dirc = fname[:-len(fname.split("/")[-1])]
    if not os.path.exists(dirc) and dirc!="":
        os.mkdir(dirc)
        
    file1 = gzip.open("%s_CH1.txt.gz" %(fname),"wb",6)
    file2 = gzip.open("%s_CH2.txt.gz" %(fname),"wb",6)

    for i in range(Nevents):
        osc.write("ACQuire:STATE STOP")

        savewaveform(file1,1)
        print('CH1 saved %s/%s'%(i+1,Nevents))

        savewaveform(file2,2)
        print('CH2 saved %s/%s'%(i+1,Nevents))

        osc.write("ACQuire:STATE RUN")

    file1.close()
    file2.close()

def Get_waveform(fname,Nevents,CH):

    dirc = fname[:-len(fname.split("/")[-1])]
    if not os.path.exists(dirc) and dirc!="":
        os.mkdir(dirc)

    file1 = gzip.open(fname+"_CH"+str(CH)+".txt.gz","wb",6)

    for i in range(Nevents):
        osc.write("ACQuire:STATE STOP")

        savewaveform(file1,CH)
        print('CH'+str(CH)+' saved %s/%s'%(i+1,Nevents))

        time.sleep(0.2)  #before (1)

        osc.write("ACQuire:STATE RUN")

    file1.close()

def initialize():   #MSO-4054B PMT試験用　初期設定

    print(" Setting up the oscilloscope MSO4054B ................................. ")
    
    # Time scale Setting
    osc.write("HORizontal:SCAle 40.0000E-9")      #TIMEBASE : 40.0ns/div
    osc.write("HORizontal:DELay:TIMe 152.4000E-9") # horizontal delay time (position) 
    osc.write("HORizontal:SAMPLERate 2.5000E+9")  # 2.50GS/s
    osc.write("HORizontal:RECOrdlength 1000000")  # 1M points

    """
    osc.write("HIStogram:MODe OFF")
    osc.write("HIStogram:DISplay LINEAR") #the scaling of the histogram data display to be the count of each histogram bin.
    osc.write("HIStogram:BOX 282.000E-9,35.2000E-3,316.4000E-9,2.4000E-3")
    osc.write("HIStogram:SOUrce CH2")
    """

    # Measure Setting
    osc.write("MEASUrement:STATIstics:MODe ON") #ON turns on statistics and displays all statistics for each measurement.
    osc.write("MEASUrement:STATIstics:WEIghting 300") #the number of samples used for the mean and standard deviation.
    osc.write("MEASUrement:METHod HISTOGRAM") #HIStogram sets the high and low waveform levels statistically using a histogram.
    osc.write("MEASUrement:GATing CURSOR")
    osc.write("MEASUrement:REFLevel:METHod PERCENT")
    osc.write("MEASUrement:REFLevel:PERCent:HIGH 90.0000")
    osc.write("MEASUrement:REFLevel:PERCent:MID1 50.0000")
    osc.write("MEASUrement:REFLevel:PERCent:MID2 50.0000")
    osc.write("MEASUrement:REFLevel:PERCent:LOW 20.0000")

    osc.write("MEASUrement:MEAS1:SOURCE1 CH2")
    osc.write("MEASUrement:MEAS2:SOURCE1 CH2")
    osc.write("MEASUrement:MEAS3:SOURCE1 CH2")
    osc.write("MEASUrement:MEAS1:TYPe MEAN")
    osc.write("MEASUrement:MEAS2:TYPe AREA")
    osc.write("MEASUrement:MEAS3:TYPe HIGH")
    osc.write("MEASUrement:MEAS1:STATE ON")
    osc.write("MEASUrement:MEAS2:STATE ON")
    osc.write("MEASUrement:MEAS3:STATE ON")

    # Trigger Setting
    osc.write("TRIGger:A:TYPe EDGE")
    osc.write("TRIGger:A:EDGE:SOUrce AUX")
    osc.write("TRIGger:A:EDGE:SLOpe RISE")
    osc.write("TRIGger:A:level 839.0000E-3")
    osc.write("TRIGger:A:mode AUTO")
    #osc.write("AUXin:PRObe:GAIN 1.0000")
    osc.write("TRIGger:A:HOLDoff:TIMe 20.0000E-9")

    # CH1 Setting
    osc.write("SELect:CH1 ON")
    osc.write("CH1:BANdwidth FULl")
    osc.write("CH1:COUPling DC")
    osc.write("CH1:INVert OFF")
    osc.write("CH1:OFFSet 0.0")
    osc.write("CH1:POSition -2.0400")
    osc.write("CH1:SCAle 10.0000E-3")
    osc.write("CH1:TERmination 50.0000")

    # CH2 Setting
    osc.write("SELect:CH2 ON")
    osc.write("CH2:BANdwidth FULl")
    osc.write("CH2:COUPling DC")
    osc.write("CH2:INVert OFF")
    osc.write("CH2:OFFSet 0.0")
    osc.write("CH2:POSition -4.0400")
    osc.write("CH2:SCAle 5.0000E-3")
    osc.write("CH2:TERmination 50.0000")

    # CH3 Setting
    osc.write("SELect:CH3 OFF")

    # CH4 Setting
    osc.write("SELect:CH4 OFF")

    # Cursors Setting
    osc.write("CURSor:FUNCtion WAVEFORM")   #Cursors : Waveform
    osc.write("CURSor:MODe INDEPENDENT")    #Linked : off
    osc.write("CURSor:SOUrce AUTO")         #Source : Auto
    osc.write("CURSor:VBArs:POSITION1 76.0E-9")     #the horizontal position <a> cursor
    osc.write("CURSor:VBArs:POSITION2 106.8000E-9") #the horizontal position <b> cursor
    osc.write("CURSor:VBArs:UNIts SECONDS")
    osc.write("CURSor:HBArs:UNIts BASE")

    # Setting waveform length , npoints = 1000000(1MS)
    osc.write("data:start 1")
    osc.write("data:stop 1000000")
    # data? b'REF1;RIBINARY;CH1;499809;499886;2\n' 
    #osc.write("data SNAP") #if set to SNAP , adjast periods between cursors


def Get_measure(fname,row,comm):    # ex.) Get_measure("filename",3,"10deg")

    dirc = fname[:-len(fname.split("/")[-1])]
    if not os.path.exists(dirc) and dirc!="":
        os.mkdir(dirc)
        
    filem = open(fname+'_measure.txt','a')

    filem.write(str(comm)+",")

    for i in range(row):
        osc.write("MEASUREMENT:MEAS%s:value?"%str(i+1))
        filem.write(osc.read().decode()[:-1]+",")
        osc.write("MEASUREMENT:MEAS%s:MEAN?"%str(i+1))
        filem.write(osc.read().decode()[:-1]+",")
        osc.write("MEASUREMENT:MEAS%s:MINImum?"%str(i+1))
        filem.write(osc.read().decode()[:-1]+",")
        osc.write("MEASUREMENT:MEAS%s:MAXimum?"%str(i+1))
        filem.write(osc.read().decode()[:-1]+",")
        osc.write("MEASUREMENT:MEAS%s:STDdev?"%str(i+1))
        filem.write(osc.read().decode()[:-1]+",")
    filem.write("\n")
    filem.close()

def close():
    osc.close()

####################################################################

osc = MSO4054B()
osc.open('TCPIP0::192.168.1.1::inst0::INSTR')

#init mso
initialize()

osc.write('WFMInpre:BYT_Nr 2')
osc.write("WFMOutpre:BYT_Nr 2")
osc.write("ACQuire:STATE RUN")

print(" Done! \n the oscilloscope MSO4054B is ready ................................. ")


if __name__ == '__main__':
    time.sleep(1)
