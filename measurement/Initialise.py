import target_driver
import target_io
import time


def Initialise(board):

    for asic in range(0, 4):
        
        board.WriteASICSetting("SSPinLE_Delay",         asic, 0x2e)
        board.WriteASICSetting("SSPinTE_Delay",         asic, 0x3d)

        board.WriteASICSetting("WR_ADDR_Incr1LE_Delay", asic, 0x3f)
        board.WriteASICSetting("WR_ADDR_Incr1TE_Delay", asic, 14)
        board.WriteASICSetting("WR_STRB1LE_Delay",      asic, 0x23)
        board.WriteASICSetting("WR_STRB1TE_Delay",      asic, 0x2d)
        board.WriteASICSetting("WR_ADDR_Incr2LE_Delay", asic, 0x25)
        board.WriteASICSetting("WR_ADDR_Incr2TE_Delay", asic, 0x34)
        board.WriteASICSetting("WR_STRB2LE_Delay",      asic, 2)
        board.WriteASICSetting("WR_STRB2TE_Delay",      asic, 12)
        
        board.WriteASICSetting("VtrimT",                asic, 0x4d8)
        board.WriteASICSetting("SSToutFB_Delay",        asic, 0x03a)

    time.sleep(0.005)


def EnableDLLFeedback(board):

    board.WriteRegister(0x33, 0x00180000)
    board.WriteRegister(0x33, 0x80180000)
    board.WriteRegister(0x33, 0x00100000)
    board.WriteSetting("Start_TimeBase", 0x1)

    time.sleep(0.1)
    
    for asic in range(0, 4):
        
        board.WriteASICSetting("Vqbuff",  asic, 0x426)
        board.WriteASICSetting("Qbias",   asic, 0x5DC)
        board.WriteASICSetting("VadjN",   asic, 2100)
        board.WriteASICSetting("VadjN",   asic, 0x8bb)
        board.WriteASICSetting("VANbuff", asic, 0x000)
        
    board.WriteRegister(0x33, 0x0)
