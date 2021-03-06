import sys
import time

import target_driver
import target_io
import Initialise

def Takedata(outfile, wforms, runid, vped):
    start = time.time()
    SleepTime = int(wforms) / 119. # send trigger ~120 Hz
    runID = runid   
    Vped = int((int(vped) - 19.2) / 0.6)
    #Vped = int((int(vped) - 21) / 0.6)
    #Vped = vped

    
    my_ip = "192.168.1.22"
    board_ip = "192.168.0.173"

    board_def = "/Users/yusukekuroda/TargetDriver_build/config/TM7_FPGA_Firmware0xA0000100.def"
    asic_def = "/Users/yusukekuroda/TargetDriver_build/config/older_firmware/TM7_ASIC.def"
    board = target_driver.TargetModule(board_def, asic_def, 1)


    # #Initialise
    if runID == 0:
        
        board.EstablishSlowControlLink(my_ip, board_ip)
        board.Initialise()
        Initialise.Initialise(board)
        Initialise.EnableDLLFeedback(board)
        
        board.WriteSetting("SetDataPort", 8107)
        board.WriteSetting("SetSlowControlPort", 8201)
        
    else:
        
        board.ReconnectToServer(my_ip, 8201, board_ip, 8105)

    # #Set Vped
    board.WriteSetting("Vped_value", Vped)
    print("Setting ground level to %d counts"%Vped)


    # #Set trigger
    board.WriteSetting("TriggerDelay",       352) #set 352 Row and Colomn 0, set 128 Row and Colomn 1
    board.WriteSetting("TACK_TriggerType",   0x0)
    board.WriteSetting("TACK_TriggerMode",   0x0)
    board.WriteSetting("TACK_EnableTrigger", 0x10000)

    board.WriteSetting("EnableChannel0", 0xffffffff)
    board.WriteSetting("EnableChannel1", 0xffffffff)
    board.WriteSetting("Zero_Enable",    0x1)

    NumberOfBuffers = 13 #(NumberOfBuffers + 1) * 32 + number of samples, maximum of T7M is 448 samples
    board.WriteSetting("NumberOfBuffers", NumberOfBuffers)


    # #Set HV
    board.WriteSetting("HV_Enable", 0x1)
    time.sleep(0.1)
    board.WriteRegister(0x20,       0x7300080f)
    board.WriteRegister(0x20,       0x7300080f)
    time.sleep(5)

    kNPacketsPerEvent = 64 # Number of read channel
    kPacketSize = ((NumberOfBuffers+1) * 64) + 22
    kBufferDepth = 10000

    listener =target_io.DataListener(kBufferDepth, kNPacketsPerEvent, kPacketSize)
    buf = listener.GetEventBuffer()
    listener.AddDAQListener(my_ip)
    
    writer = target_io.EventFileWriter(outfile, kNPacketsPerEvent, kPacketSize)
    
    listener.StartListening()
    writer.StartWatchingBuffer(buf)

    board.WriteSetting("ExtTriggerDirection", 0x0)
    time.sleep(SleepTime)
    #board.WriteSetting("ExtTriggerDirection", 0x1)

    writer.StopWatchingBuffer()       
    listener.StopListening()
    
    time.sleep(3)
    
    #board.WriteSetting("HV_Enable", 0x0)
    board.CloseSockets()    
    buf.Flush()
    writer.Close()
    print("Finished reading from TARGET")
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
