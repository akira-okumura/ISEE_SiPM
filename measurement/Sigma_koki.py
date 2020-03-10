"""
This is an interface module for instruments produced by Sigma Koki
"""

import builtins as exceptions
import serial
import sys

class GSC02(object):
    """
    Stage controller GSC-02
    """
    def __init__(self):
        self.__baudRate = 9600 # 9600 bps
        self.__parityBit = 'N' # None
        self.__dataBit = 8
        self.__stopBit = 1
        self.__rtscts = True

    def setBaudRate(self, rate):
        if rate in (2400, 4800, 9600, 19200):
            self.__baudRate = rate
        else:
            raise exceptions.ValueError('Invalid buard rate %d was given. Must be chosen from 2400/4800/9600/19200.' % rate)

    def open(self, port, readTimeOut = 1, writeTimeOut = 1):
        self.serial = serial.Serial(port         = port,
                                    baudrate     = self.__baudRate,
                                    bytesize     = self.__dataBit,
                                    parity       = self.__parityBit,
                                    stopbits     = self.__stopBit,
                                    timeout      = readTimeOut,
                                    writeTimeout = writeTimeOut,
                                    rtscts       = self.__rtscts)

    def write(self, command):
        btemp = command + '\r\n'
        self.serial.write(btemp.encode())

    def readline(self):
        return self.serial.readline()[:-2]

    def returnToMechanicalOrigin(self, stage1, stage2):
        """
        Moves the stages to the +/- end points and reset the coordinate values
        to zero.
        """
        if stage1 == '+' and stage2 == '+':
            self.write('H:W++')
        elif stage1 == '+' and stage2 == '-':
            self.write('H:W+-')
        elif stage1 == '-' and stage2 == '+':
            self.write('H:W-+')
        elif stage1 == '-' and stage2 == '-':
            self.write('H:W--')
        elif stage1 == '+':
            self.write('H:1+')
        elif stage1 == '-':
            self.write('H:1-')
        elif stage2 == '+':
            self.write('H:2+')
        elif stage2 == '-':
            self.write('H:2-')
        else:
            return

    def move(self, stage1, stage2):
        """
        Moves the stages with the specified values. Since GSC-02 is a half-step
        stepping driver, 1 pulse corresponds to "half-step movement" in the
        stage catalogues.
        """
        if not (-16777214 <= stage1 <= 16777214):
            raise exceptions.ValueError('stage1 must be between -16777214 and 16777214.')

        if not (-16777214 <= stage2 <= 16777214):
            raise exceptions.ValueError('stage2 must be between -16777214 and 16777214.')

        command = 'M:W'
        if stage1 >= 0:
            command += '+P%d' % stage1
        else:
            command += '-P%d' % -stage1

        if stage2 >= 0:
            command += '+P%d' % stage2
        else:
            command += '-P%d' % -stage2

        self.write(command)
        self.go()

    def jog(self, stage1, stage2):
        """
        Moves the stages continuously at the minimum speed.
        stage1: '+' positive direction, '-' negative direction
        stage2: '+' positive direction, '-' negative direction
        If other values are given, stages will not move.
        """
        if stage1 == '+' and stage2 == '+':
            self.write('J:W++')
        elif stage1 == '+' and stage2 == '-':
            self.write('J:W+-')
        elif stage1 == '-' and stage2 == '+':
            self.write('J:W-+')
        elif stage1 == '-' and stage2 == '-':
            self.write('J:W--')
        elif stage1 == '+':
            self.write('J:1+')
        elif stage1 == '-':
            self.write('J:1-')
        elif stage2 == '+':
            self.write('J:2+')
        elif stage2 == '-':
            self.write('J:2-')
        else:
            return
        
        self.go()

    def go(self):
        """
        Moves the stages. To be used internally.
        """
        self.write('G')

    def decelerate(self, stage1, stage2):
        """
        Decelerates and stop the stages. 
        """
        if stage1 and stage2:
            self.write('L:W')
        elif stage1:
            self.write('L:1')
        elif stage2:
            self.write('L:2')

    def stop(self):
        """
        Stops the stages immediately.
        """
        self.write('L:E')

    def initializeOrigin(self, stage1, stage2):
        """
        Sets the origin to the current position.
        stage1: If true, set the origin of the stage 1 to the current position
        stage2: If true, set the origin of the stage 1 to the current position
        """
        if stage1:
            self.write('R:1')

        if stage2:
            self.write('R:2')

    def setSpeed(self, highspeed, minSpeed1, maxSpeed1, accelerationTime1,
                 minSpeed2, maxSpeed2, accelerationTime2):
        """
        Sets the movement speeds of the stages
        highspeed: If true, speed range is 50-20000, else 1-200
        minSpeed1/2: Minimum speed (PPS)
        maxSpeed1/2: Maximum speed (PPS)
        accelerationTime1/2: Acceleration time to be taken from min to max (ms)

        |      _________        ... maximum speed (PPS)
        |    /          \
        |   /            \
        |  /              \     ... minimum speed (PPS)
        |  |              |
        |  |              |
        |__|______________|________
           <->              acceleration time (ms)
                        <-> deceleration time (ms)
        """
        if not highspeed:
            if not (1 <= minSpeed1 <= maxSpeed1 <= 200):
                raise exceptions.ValueError('Must be 1 <= minSpeed1 <= maxSpeed1 <= 200 in low speed range.')
            if not (1 <= minSpeed2 <= maxSpeed2 <= 200):
                raise exceptions.ValueError('Must be 1 <= minSpeed2 <= maxSpeed2 <= 200 in low speed range.')
        else:
            if not (50 <= minSpeed1 <= maxSpeed1 <= 20000):
                raise exceptions.ValueError('Must be 50 <= minSpeed1 <= maxSpeed1 <= 20000 in high speed range.')
            if not (50 <= minSpeed2 <= maxSpeed2 <= 20000):
                raise exceptions.ValueError('Must be 50 <= minSpeed2 <= maxSpeed2 <= 20000 in high speed range.')

        if not (0 <= accelerationTime1 <= 1000):
            raise exceptions.ValueError('Must be 00 <= accelerationTime1 <= 1000.')

        if not (0 <= accelerationTime2 <= 1000):
            raise exceptions.ValueError('Must be 00 <= accelerationTime2 <= 1000.')

        if highspeed:
            self.write('D:2S%dF%dR%dS%dF%dR%d' % (minSpeed1, maxSpeed1, accelerationTime1, minSpeed2, maxSpeed2, accelerationTime2))
        else:
            self.write('D:1S%dF%dR%dS%dF%dR%d' % (minSpeed1, maxSpeed1, accelerationTime1, minSpeed2, maxSpeed2, accelerationTime2))

    def enableMotorExcitation(self, stage1 = True, stage2 = False):
        """
        Enables motor excitation
        """
        if stage1 in (True, False):
            self.write('C:1%d' % stage1)

        if stage2 in (True, False):
            self.write('C:2%d' % stage2)

    def getStatus(self):
        """
        Returns the status of the controller
        """
        self.write('Q:')
        atemp = self.readline()
        atemp = str(atemp).replace("'","")
        atemp = atemp.replace('b','')        
        return atemp

    def getACK3(self):
        """
        Returns the status of ACK3
        """
        self.write('!:')
        atemp = self.readline()
        atemp = str(atemp).replace("'","")
        atemp = atemp.replace('b','')        
        return atemp

    def getVersion(self):
        """
        Returns the ROM version
        """
        self.write('?:V')
        atemp = self.readline()
        atemp = str(atemp).replace("'","")
        atemp = atemp.replace('b','')        
        return atemp

    
class SHOT702(object):
    """
    Stage controller SHOT-702
    written by YK
    """
    def __init__(self):
        self.__baudRate = 38400 # 38400 bps
        self.__parityBit = 'N' # None
        self.__dataBit = 8
        self.__stopBit = 1
        self.__rtscts = True

    def setBaudRate(self, rate): # changed by YK
        if rate in (38400):
            self.__baudRate = rate
        else:
            raise exceptions.ValueError('Invalid buard rate %d was given. Must be chosen from 38400.' % rate)    

    def open(self, port, readTimeOut = 1, writeTimeOut = 1):
        self.serial = serial.Serial(port         = port,
                                    baudrate     = self.__baudRate,
                                    bytesize     = self.__dataBit,
                                    parity       = self.__parityBit,
                                    stopbits     = self.__stopBit,
                                    timeout      = readTimeOut,
                                    writeTimeout = writeTimeOut,
                                    rtscts       = self.__rtscts)

    def write(self, command):
        btemp = command + '\r\n'
        self.serial.write(btemp.encode())

        """
        SHOT702 reply b'OK' or b'NG' 
        written by YK
        """
        atemp = self.readline()
        atemp = str(atemp).replace("'","")
        atemp = atemp.replace('b','')
        if atemp == 'NG':
            raise exceptions.ValueError('Device was not accepted properly')

    def checkwrite(self, command):
        """
        Used for commands that return data
        written by YK
        """
        btemp = command + '\r\n'
        self.serial.write(btemp.encode())

        atemp = self.readline()
        atemp = str(atemp).replace("'","")
        atemp = atemp.replace('b','')
        return atemp
        
    def readline(self):
        return self.serial.readline()[:-2]

    def returnToMechanicalOrigin(self, stage1, stage2):
        """
        Moves the stages to the end points and reset the coordinate values
        to zero.
        written by YK
        """
        if stage1 == 1 and stage2 == 1:
            self.write('H:W')
        elif stage1 == 1:
            self.write('H:1')
        elif stage2 == 1:
            self.write('H:2')
        else:
            return

    def move(self, stage1, stage2):
        """
        Moves the stages with the specified values. Since SHOT-702 is a half-step
        stepping driver, 1 pulse corresponds to "half-step movement" in the
        stage catalogues.
        """
        if not (-16777214 <= stage1 <= 16777214):
            raise exceptions.ValueError('stage1 must be between -16777214 and 16777214.')

        if not (-16777214 <= stage2 <= 16777214):
            raise exceptions.ValueError('stage2 must be between -16777214 and 16777214.')

        command = 'M:W'
        if stage1 >= 0:
            command += '+P%d' % stage1
        else:
            command += '-P%d' % -stage1

        if stage2 >= 0:
            command += '+P%d' % stage2
        else:
            command += '-P%d' % -stage2

        self.write(command)
        self.go()

    def jog(self, stage1, stage2):
        """
        Moves the stages continuously at the minimum speed.
        stage1: '+' positive direction, '-' negative direction
        stage2: '+' positive direction, '-' negative direction
        If other values are given, stages will not move.
        """
        if stage1 == '+' and stage2 == '+':
            self.write('J:W++')
        elif stage1 == '+' and stage2 == '-':
            self.write('J:W+-')
        elif stage1 == '-' and stage2 == '+':
            self.write('J:W-+')
        elif stage1 == '-' and stage2 == '-':
            self.write('J:W--')
        elif stage1 == '+':
            self.write('J:1+')
        elif stage1 == '-':
            self.write('J:1-')
        elif stage2 == '+':
            self.write('J:2+')
        elif stage2 == '-':
            self.write('J:2-')
        else:
            return
        
        self.go()

    def go(self):
        """
        Moves the stages. To be used internally.
        """
        self.write('G')

    def decelerate(self, stage1, stage2):
        """
        Decelerates and stop the stages. 
        """
        if stage1 and stage2:
            self.write('L:W')
        elif stage1:
            self.write('L:1')
        elif stage2:
            self.write('L:2')

    def stop(self):
        """
        Stops the stages immediately.
        """
        self.write('L:E')

    def initializeOrigin(self, stage1, stage2):
        """
        Sets the origin to the current position.
        stage1: If true, set the origin of the stage 1 to the current position
        stage2: If true, set the origin of the stage 1 to the current position
        """
        if stage1:
            self.write('R:1')

        if stage2:
            self.write('R:2')

    def setSpeed(self, minSpeed, maxSpeed, accelerationTime):
        """
        Sets the movement speeds of the stages
        minSpeed: Minimum speed (PPS)
        maxSpeed: Maximum speed (PPS)
        accelerationTime: Acceleration time to be taken from min to max (ms)     
        written by YK    
        """
        if not (1 <= minSpeed <= maxSpeed <= 500000):
                raise exceptions.ValueError('Must be 1 <= minSpeed1 <= maxSpeed1 <= 500000.')

        if not (0 <= accelerationTime <= 1000):
            raise exceptions.ValueError('Must be 00 <= accelerationTime <= 1000.')

        self.write('D:WS%dF%dR%dS%dF%dR%d' % (minSpeed, maxSpeed, accelerationTime, minSpeed, maxSpeed, accelerationTime))


    def enableMotorExcitation(self, stage1 = True, stage2 = False):
        """
        Enables motor excitation
        """
        if stage1 in (True, False):
            self.write('C:1%d' % stage1)

        if stage2 in (True, False):
            self.write('C:2%d' % stage2)

    def getStatus(self):
        """
        Returns the status of the controller
        written by YK
        """
        return self.checkwrite('Q:')

    def getACK3(self):
        """
        Returns the status of ACK3
        written by YK
        """
        return self.checkwrite('!:')

    def getVersion(self):
        """
        Returns the ROM version
        written by YK
        """
        return self.checkwrite('?:V')

    def getBaseRate(self, stage1 = True, stage2 = False):
        """
        Returns the Base Rate 
        written by YK
        """
        if stage1 and stage2:
            return self.checkwrite('?:PW')
        elif stage1:
            return self.checkwrite('?:P1')
        elif stage2:
            return self.checkwrite('?:P2')
            
    def getDivide(self, stage1 = True, stage2 = False):
        """
        Returns the Divide number 
        written by YK
        """
        if stage1 and stage2:
            return self.checkwrite('?:SW')
        elif stage1:
            return self.checkwrite('?:S1')
        elif stage2:
            return self.checkwrite('?:S2')
        
    def getSpeed(self, stage1 = True, stage2 = False):
        """
        Returns the Speed 
        written by YK
        """
        if stage1 and stage2:
            return self.checkwrite('?:DW')
        elif stage1:
            return self.checkwrite('?:D1')
        elif stage2:
            return self.checkwrite('?:D2')  
    
    def getORGSpeed(self, stage1 = True, stage2 = False):
        """
        Returns the ORG speed 
        written by YK
        """
        if stage1 and stage2:
            return self.checkwrite('?:BW')
        elif stage1:
            return self.checkwrite('?:B1')
        elif stage2:
            return self.checkwrite('?:B2')
