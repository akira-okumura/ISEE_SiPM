import usbtc08
import ctypes
import time

# from usbtc08 import *

# TC_08.GetTemp() : return calibrated Temp[0-7]
# TC_08.GetTemp_raw() : return raw Temp[0-7]
# TC_08.USB_Close() : USB Connection Close
# TC_08.USB_Open() : USB Connection Open

Nch = 8
usb = usbtc08.USBTC08()
usb.Open()
unitInfo = usb.GetUnitInfo()
usb.SetChannel(usbtc08.USBTC08_CHANNEL_CJC, b'C')
for i, ch in enumerate((usbtc08.USBTC08_CHANNEL_1, usbtc08.USBTC08_CHANNEL_2, usbtc08.USBTC08_CHANNEL_3, usbtc08.USBTC08_CHANNEL_4,
                        usbtc08.USBTC08_CHANNEL_5, usbtc08.USBTC08_CHANNEL_6, usbtc08.USBTC08_CHANNEL_7, usbtc08.USBTC08_CHANNEL_8)):
    usb.SetChannel(ch, b'K') # type K thermocouple

temp = (ctypes.c_float*(usbtc08.USBTC08_MAX_CHANNELS + 1))()
overflow_flags = (ctypes.c_int16*(usbtc08.USBTC08_MAX_CHANNELS + 1))()
units = usbtc08.USBTC08_UNITS_CENTIGRADE

p0= [0.7909999999999717, 0.7059999999999411, 0.6559999999999663, 0.5619999999999893, 0.6520000000000342, 0.814999999999961, 0.8729999999999969, 0.8869999999999225]
p1= [0.9878000000000011, 0.9896000000000023, 0.9888000000000012, 0.9876000000000005, 0.9835999999999986, 0.9834000000000015, 0.9830000000000001, 0.983800000000003]
# cal_temp = (measured_tempTC08 - p0)/p1


def GetTemp():
    f_temp = []
    usb.GetSingle(temp, overflow_flags, units)
    for i, ch in enumerate((usbtc08.USBTC08_CHANNEL_1, usbtc08.USBTC08_CHANNEL_2, usbtc08.USBTC08_CHANNEL_3, usbtc08.USBTC08_CHANNEL_4,
                            usbtc08.USBTC08_CHANNEL_5, usbtc08.USBTC08_CHANNEL_6, usbtc08.USBTC08_CHANNEL_7, usbtc08.USBTC08_CHANNEL_8)):

        f_temp.append(round(float(temp[ch]),2))

    for j in range(Nch):
        f_temp[j] = round((f_temp[j] - p0[j])/p1[j],2)

    return f_temp        

def GetTemp_raw():
    f_temp = []
    usb.GetSingle(temp, overflow_flags, units)
    for i, ch in enumerate((usbtc08.USBTC08_CHANNEL_1, usbtc08.USBTC08_CHANNEL_2, usbtc08.USBTC08_CHANNEL_3, usbtc08.USBTC08_CHANNEL_4,
                            usbtc08.USBTC08_CHANNEL_5, usbtc08.USBTC08_CHANNEL_6, usbtc08.USBTC08_CHANNEL_7, usbtc08.USBTC08_CHANNEL_8)):

        f_temp.append(round(float(temp[ch]),2))

    return f_temp  

def USB_Open():
    usb.Open()

def USB_Close(): 
    usb.Close()


if __name__ == '__main__':
    time.sleep(1)