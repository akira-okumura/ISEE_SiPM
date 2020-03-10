import serial, time

class GPDs(object):
    """
    class to control GPD-3303s by serial
    """
    def __init__(self):
        self.__baudRate = 9600 # 9600 bps
        self.__parityBit = 'N' # None
        self.__dataBit = 8
        self.__stopBit = 1

    def setBaudRate(self, rate):
        if rate in (9600, 57600, 115200):
            self.__baudRate = rate
        else:
            raise ValueError('Invalid bard rate %d was given. Must be chosen from 9600/57600/115200' % rate)

    def open(self, port, readTimeOut = 1, writeTimeOut = 1):
        self.serial = serial.Serial(port = port,
                                    baudrate = self.__baudRate,
                                    bytesize = self.__dataBit,
                                    parity = self.__parityBit,
                                    stopbits = self.__stopBit,
                                    timeout = readTimeOut,
                                    writeTimeout = writeTimeOut)

    def write(self, command):
        btemp = command + '\r\n'
        self.serial.write(btemp.encode())
        time.sleep(0.1)

    def readline(self):
        return self.serial.readline()[:-2]
        time.sleep(0.1)
        
    def setOutputON(self):
        self.write('OUT1')

    def setOutputOFF(self):
        self.write('OUT0')

    def setVSET(self, channel, V):
        command = 'VSET%d:%f' % (channel, V)
        self.write(command)

    def getVSET(self, channel):
        command = 'VSET%d?' % channel
        self.write(command)
        atemp = self.readline()
        atemp = str(atemp).replace("'", "")
        atemp = atemp.replace('b', '')
        return atemp

    def getVOUT(self, channel):
        command = 'VOUT%d?' % channel
        self.write(command)
        
        atemp = self.readline()
        atemp = str(atemp).replace("'", "")
        atemp = atemp.replace('b', '')
        return atemp
        
    def setISET(self, channel, I):
        command = 'ISET%d:%f' % (channel, I)
        self.write(command)
        
    def getISET(self, channel):
        command = 'ISET%d?' % channel
        self.write(command)

        atemp = self.readline()
        atemp = str(atemp).replace("'", "")
        atemp = atemp.replace('b', '')
        return atemp
        
    def getIOUT(self, channel):
        command = 'IOUT%d?' % channel
        self.write(command)

        atemp = self.readline()
        atemp = str(atemp).replace("'", "")
        atemp = atemp.replace('b', '')
        return atemp


    def getStatus(self):
        self.write('STATUS?')
        atemp = self.readline()
        atemp = str(atemp).replace("'", "")
        atemp = atemp.replace('b', '')
        return atemp

        
    def close(self):
        self.serial.close()
        
