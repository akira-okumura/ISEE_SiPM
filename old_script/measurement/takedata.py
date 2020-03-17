import target_driver
import target_io
import time
import Initialise
import sys

if __name__=="__main__":

    args = sys.argv
    outfile = str(args[1])
    SleepTime = int(args[2]) / 119. # send trigger ~120 Hz
    runID = int(args[3])    
    Vped = int((int(args[4]) - 21) / 0.6)
    
    my_ip = "192.168.1.2"
    board_ip = "192.168.0.173"

    board_def = "/Users/az/Documents/TargetDriver_20763/config/TM7_FPGA_Firmware0xA0000100.def"
    asic_def = "/Users/az/Documents/TargetDriver_20763/config/older_firmware/TM7_ASIC.def"
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
