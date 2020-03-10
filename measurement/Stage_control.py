import serial, sys, time, os, gzip, math
import Sigma_koki
import numpy as np


class Stage(object):
    def __init__(self):
        #self.Range_Speed = 1
        self.Min_Speed = 50
        self.Max_Speed = 20000
        
        self.w_x = 1000 / 2. #/1mm SGSP 33-200
        self.w_z = 1000 / 6. #/1mm SGSP 26-200
        self.w_angle = 1 / 0.0025 #/deg OSMS-60YAW

    def Open(self):
        #LED-XZ stage
        self.gscXZ = Sigma_koki.SHOT702()
        self.gscXZ.open('/dev/tty.usbserial-FTRTNFQI')
        
        if self.gscXZ.getStatus() == '':
            raise ValueError('XZstage is invalid')
        
        #TARGET-rotation stage
        self.gscT = Sigma_koki.GSC02()
        self.gscT.open('/dev/tty.usbserial-FTRTNEFZ')
        
        if self.gscT.getStatus() == '':
            raise ValueError('Rotation stage is invalid')
        
        #self.gscT.returnToMechanicalOrigin('+', '-')
        
    def Set_Speed_parameter(self, rang, minS, maxS):
        #self.Range_Speed = rang
        self.Min_Speed = minS
        self.Max_Speed = maxS
            
    def stageX_Relative(self, n, AccelerationSpeed):
        self.gscXZ.setSpeed(self.Min_Speed, self.Max_Speed, AccelerationSpeed)
        
        self.gscXZ.move(0, n * self.w_x) 
        time.sleep(6)
        
        a = self.gscXZ.getStatus()
        count = int(a[12:21])
        
        operation_vale = count / self.w_x
        print (" operation value of LED stageX = ", operation_vale, "(mm)")
        
    def stageX(n, AccelerationSpeed):
        self.gscXZ.returnToMechanicalOrigin(0, 1) # (0, Xstage) #
        
        while 1:
            aaa = self.gscXZ.getStatus()
            if aaa[-1] == 'R':
                break    
        time.sleep(1)
            
        self.gscXZ.setSpeed(self.Min_Speed, self.Max_Speed, AccelerationSpeed)
    
        self.gscXZ.move(0, n * self.w_x) 
        time.sleep(6)
        
        a = self.gscXZ.getStatus()
        count = int(a[12:21])

        operation_vale = count / self.w_x
        print (" operation value of LED stageX = ", operation_vale, "(mm)")

    def stageZ_Relative(self, n, AccelerationSpeed):
        self.gscXZ.setSpeed(self.Min_Speed, self.Max_Speed, AccelerationSpeed)

        self.gscXZ.move(n * self.w_z, 0) 
        time.sleep(4)

        a = self.gscXZ.getStatus()
        count = int(a[1:10])

        operation_vale = count / self.w_z
        print (" operation value of LED stageZ = ", operation_vale, "(mm)")

    def stageZ(self, n, AccelerationSpeed):
        self.gscXZ.returnToMechanicalOrigin(1, 0) # (Zstage, 0) #
        while 1:
            aaa = self.gscXZ.getStatus()
            if aaa[-1] == 'R':
                break  
        time.sleep(1)
    
        self.gscXZ.setSpeed(self.Min_Speed, self.Max_Speed, AccelerationSpeed)

        self.gscXZ.move(n * self.w_z, 0) 
        time.sleep(4)

        a = self.gscXZ.getStatus()
        count = int(a[1:10])

        operation_vale = count / self.w_z
        print (" operation value of LED stageZ = ", operation_vale, "(mm)")

    def rotation_initialize(self):
        self.gscT.returnToMechanicalOrigin('-', 0) # (theta_stage, 0) #

        #print (" operation value of theta_stage = ", gscA.getStatus(), "(mm)") 

    def rotation_initialize0deg(self):
        self.gscT.returnToMechanicalOrigin('-', 0) # (theta_stage, 0) #

        while 1:
            aaa = self.gscT.getStatus()
            if aaa[-1] == 'R':
                break  
        time.sleep(2)

        self.rotation_Relative(90., 50) # must be set to TARGET

        while 1:
            aaa = self.gscT.getStatus()
            if aaa[-1] == 'R':
                break  
        time.sleep(2)

        self.Set0pointAngle()
        self.rotation_Relative(0, 50)
        
    def rotation_Relative(self, angle, AccelerationSpeed):

        self.gscT.setSpeed(1, 50, 5000, AccelerationSpeed, 50, 5000, AccelerationSpeed) #MaxSpeed 20000 is bad for OSMS-60YAW

        self.gscT.move(angle * self.w_angle, 0)
        time.sleep(4)

        while 1:
            aaa = self.gscT.getStatus()
            if aaa[-1] == 'R':
                break
        time.sleep(2)

        a = self.gscT.getStatus()
        theta_value = int(a[1:10])

        if a[0] == '-':
            theta_value = - theta_value
        print (" Rotation Angle = ", theta_value / self.w_angle, "(deg)")

    def rotation(self, angle, AccelerationSpeed):
        
        self.gscT.returnToMechanicalOrigin('-', 0) # (theta_stage, 0) #

        while 1:
            aaa = self.gscT.getStatus()
            if aaa[-1] == 'R':
                break  
        time.sleep(1)

        self.rotation_Relative(90., 50) # must be set to TARGET

        while 1:
            aaa = self.gscT.getStatus()
            if aaa[-1] == 'R':
                break  
        time.sleep(1)

        self.Set0pointAngle()

        self.gscT.setSpeed(1, 50, 5000, AccelerationSpeed, 50, 5000, AccelerationSpeed) #MaxSpeed 20000 is bad for OSMS-60YAW

        self.gscT.move(angle * self.w_angle, 0)
        time.sleep(4)

        a = self.gscT.getStatus()
        theta_value = int(a[1:10])

        if a[0] == '-':
            theta_value = - theta_value
        print (" Rotation Angle = ", theta_value / self.w_angle, "(deg)")

    def Set0pointX(self):
        self.gscXZ.initializeOrigin(0, 1)

    def Set0pointZ(self):
        self.gscXZ.initializeOrigin(1, 0)

    def Set0pointAngle(self):
        self.gscT.initializeOrigin(1, 0)

    def stageX_initialize(self):
        '''
        changed by YK
        '''
        self.gscXZ.returnToMechanicalOrigin(0, 1) # (0, Xstage) #
        print (" operation value of theta_stage = ", self.gscXZ.getStatus(), "(mm)") 
    
    def stageZ_initialize(self):
        '''
        changed by YK
        '''
        self.gscXZ.returnToMechanicalOrigin(1, 0) # (Zstage, 0) #
        print (" operation value of theta_stage = ", self.gscXZ.getStatus(), "(mm)")

    def GetX(self):
        a = self.gscXZ.getStatus()
        count = int(a[12:21])
        return round(count / self.w_x, 1)

    def GetZ(self):
        a = self.gscXZ.getStatus()
        count = int(a[1:10])
        return round(count / self.w_z, 1)

    def GetAngle(self):
        a = self.gscT.getStatus()
        theta_value = int(a[1:10])
        if a[0] == '-':
            theta_value = - theta_value
        return round(theta_value / self.w_angle, 2)
    
    def Wait_Rotationmove(self):
        while 1:
            aaa = self.gscT.getStatus()
            if aaa[-1] == 'R':
                break  
        time.sleep(1)
            
    
if __name__ == '__main__':    

    ##########################################################
    S = Stage()
    #gscA.initializeOrigin(1,0)
    S.Open()
    S.rotation_Relative(0,50) # rotation(angle[deg],speed[50])
    S.stageX_Relative(0,50)   # stageX(distance[mm],speed[50])


    print('A Rotation Status', S.GetX(), S.GetZ())
    print('B LEDstage Status', S.GetAngle())

    exit()
    ###########################################################
