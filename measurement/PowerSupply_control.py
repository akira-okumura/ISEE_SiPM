import serial, time
import GWInstek


class PS(object):
    def Open(self):
        #Stage and TARGET GDP 3303
        self.gdpS = GWInstek.GPDs()
        self.gdpS.open('/dev/tty.usbserial-A700f6QX')

        if self.gdpS.getStatus() == '':
            raise ValueError('GDP 3303s is invalid')
        
        self.gdpS.setVSET(1, 0)
        self.gdpS.setVSET(2, 0)
                
        #PMT GDP 4303
        self.gdpP = GWInstek.GPDs()
        self.gdpP.open('/dev/tty.usbserial-A4008T7f')
        
        if self.gdpP.getStatus() == '':
            raise ValueError('GDP 4303s is invalid')

        self.gdpP.setVSET(1, 0)
        self.gdpP.setVSET(2, 0)
        self.gdpP.setVSET(3, 0)
        self.gdpP.setVSET(4, 0)
        
    def Init_TARGET(self):
        self.gdpS.setVSET(1, 12)
        self.gdpS.setISET(1, 1)

        print('CH 1: %.3f (V) %.3f (A) TARGET' % (float(self.gdpS.getVSET(1)), float(self.gdpS.getISET(1))))

    def Init_Stage(self):
        self.gdpS.setVSET(2, 24)
        self.gdpS.setISET(2, 0.5)

        print('CH 2: %.3f (V) %.3f (A) Stage' % (float(self.gdpS.getVSET(2)), float(self.gdpS.getISET(2))))
    
    def Init_PMT(self, V1, V2):
        self.gdpP.setVSET(2, V1)
        self.gdpP.setISET(2, 0.5)
        self.gdpP.setVSET(3, V2)
        self.gdpP.setISET(3, 0.5)

        print('CH 2: %.3f (V) %.3f (A) PMT1' % (float(self.gdpP.getVSET(2)[:-1]), float(self.gdpP.getISET(2)[:-1])))
        print('CH 3: %.3f (V) %.3f (A) PMT2' % (float(self.gdpP.getVSET(3)[:-1]), float(self.gdpP.getISET(3)[:-1])))

    def Init_sun(self):
        self.gdpP.setVSET(1, 5)
    
    def Initalise(self):
        self.Init_Stage()
        self.Init_TARGET()
        self.Init_PMT(6, 1.5)

    def OutputON_Stage(self):
        self.gdpS.setOutputON()
    
    def OutputON_PMT(self):
        self.gdpP.setOutputON()
                    
    def OutputON(self):
        self.gdpS.setOutputON()
        self.gdpP.setOutputON()

    def OutputOFF_Stage(self):
        self.gdpS.setOutputOFF()
    
    def OutputOFF_PMT(self):
        self.gdpP.setOutputOFF()
    
    def OutputOFF(self):
        self.gdpS.setOutputOFF()
        self.gdpP.setOutputOFF()

    def GetStatusS(self):
        return self.gdpS.getStatus()
    
    def GetStatusP(self):
        return self.gdpP.getStatus()
    
    def Close(self):
        self.gdpS.close()
        self.gdpP.close()
    

if __name__ == '__main__':
    
    ##################################################
    ps = PS()
    ps.Open()

    time.sleep(1)
    ps.Init_TARGET()
    ps.Init_Stage()
    ps.Init_PMT(0, 0)
    ps.OutputON()
    
    time.sleep(1)
    print(ps.GetStatusS())
    print(ps.GetStatusP())
    
    ps.OutputOFF()
    ps.Close()
    
    ##################################################
