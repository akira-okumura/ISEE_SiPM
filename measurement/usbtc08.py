'''
以下のコマンドで温度測定を 1 回実行します。
$ DYLD_LIBRARY_PATH=/Applications/PicoScope6.app/Contents/Resources/lib python3 usbtc08.py

事前に、PicoScope 6.12.9 をインストールしておいてください。
https://www.picotech.com/downloads/_lightbox/picoscope6mac

PicoScope6.app というアプリケーションが /Applications に入りますが、これを起動する必要はなく、そのディレクトリ内部にあるライブラリのみを利用します。

export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Applications/PicoScope6.app/Contents/Resources/lib
という行を ~/.bashrc に追加すれば、
$ python3 usbtc08.py
とするだけでも動作する
（隠しファイルの表示は、command + shift + . ）
'''

import ctypes
import ctypes.util
import sys
import time

USBTC08_MAX_FILTER_SIZE = 255
USBTC08_MAX_SAMPLE_BUFFER = 600
USBTC08_MAX_INFO_CHARS = 256
USBTC08_MAX_DATE_CHARS = 9
USBTC08_MAX_SERIAL_CHARS = 11
USBTC08_MAX_VERSION_CHARS = 12

USBTC08_PROGRESS_FAIL = -1
USBTC08_PROGRESS_PENDING = 0
USBTC08_PROGRESS_COMPLETE = 1

USBTC08_ERROR_OK = 0
USBTC08_ERROR_OS_NOT_SUPPORTED = 1
USBTC08_ERROR_NO_CHANNELS_SET = 2
USBTC08_ERROR_INVALID_PARAMETER = 3
USBTC08_ERROR_VARIANT_NOT_SUPPORTED = 4
USBTC08_ERROR_INCORRECT_MODE = 5
USBTC08_ERROR_ENUMERATION_INCOMPLETE = 6
USBTC08_ERROR_NOT_RESPONDING = 7
USBTC08_ERROR_FW_FAIL = 8
USBTC08_ERROR_CONFIG_FAIL = 9
USBTC08_ERROR_NOT_FOUND = 10
USBTC08_ERROR_THREAD_FAIL = 11
USBTC08_ERROR_PIPE_INFO_FAIL = 12
USBTC08_ERROR_NOT_CALIBRATED = 13
USBTC08_EROOR_PICOPP_TOO_OLD = 14
USBTC08_ERROR_PICO_DRIVER_FUNCTION = 15
USBTC08_ERROR_COMMUNICATION = 16

USBTC08_UNITS_CENTIGRADE = 0
USBTC08_UNITS_FAHRENHEIT = 1
USBTC08_UNITS_KELVIN = 2
USBTC08_UNITS_RANKINE = 3
USBTC08_MAX_UNITS = USBTC08_UNITS_RANKINE

USBTC08_CHANNEL_CJC = 0
USBTC08_CHANNEL_1 = 1
USBTC08_CHANNEL_2 = 2
USBTC08_CHANNEL_3 = 3
USBTC08_CHANNEL_4 = 4
USBTC08_CHANNEL_5 = 5
USBTC08_CHANNEL_6 = 6
USBTC08_CHANNEL_7 = 7
USBTC08_CHANNEL_8 = 8
USBTC08_MAX_CHANNELS = USBTC08_CHANNEL_8

class USBTC08Error(Exception):
    pass

class USBTC08Info(ctypes.Structure):
    _fields_ = [('size', ctypes.c_int16),
                ('DriverVersion', ctypes.c_char*USBTC08_MAX_VERSION_CHARS),
                ('PicoppVersion', ctypes.c_int16),
                ('HardwareVersion', ctypes.c_int16),
                ('Variant', ctypes.c_int16),
                ('szSerial', ctypes.c_char*USBTC08_MAX_SERIAL_CHARS),
                ('szCalDate', ctypes.c_char*USBTC08_MAX_DATE_CHARS)]

class USBTC08(object):
    __lib = None
   
    def __init__(self):
        if self.__lib == None:
            libname = 'usbtc08'
            path = ctypes.util.find_library(libname)
            if path == None:
                sys.stderr.write('Library %s not found\n' % libname)
                return
            try:
                self.__lib = ctypes.cdll.LoadLibrary(path)
            except OSError:
                sys.stderr.write('Cannot load library')
                return

    def Open(self):
        self.OpenUnitAsync()
        self.OpenUnitProgress()

    def GetLastError(self):
        ret = self.__lib.usb_tc08_get_last_error(self.__handle)
        if ret == -1:
            raise USBTC08Error(ret, 'Invalid handle.')
        elif ret == USBTC08_ERROR_OK:
            pass
        elif ret == USBTC08_ERROR_OS_NOT_SUPPORTED:
            raise USBTC08Error(ret, 'The driver does not support the current operating system.')
        elif ret == USBTC08_ERROR_NO_CHANNELS_SET:
            raise USBTC08Error(ret, 'A call to usb_tc08_set_channel is required.')
        elif ret == USBTC08_ERROR_INVALID_PARAMETER:
            raise USBTC08Error(ret, 'One or more of the function arguments were invalid.')
        elif ret == USBTC08_ERROR_VARIANT_NOT_SUPPORTED:
            raise USBTC08Error(ret, 'The hardware version is not supported. Download the latest driver.')
        elif ret == USBTC08_ERROR_INCORRECT_MODE:
            raise USBTC08Error(ret, 'An incompatible mix of legacy and non- legacy functions was called (or usb_tc08_get_single was called while in streaming mode).')
        elif ret == USBTC08_ERROR_ENUMERATION_INCOMPLETE:
            raise USBTC08Error(ret, 'usb_tc08_open_unit_async was called again while a background enumeration was already in progress.')
        elif ret == USBTC08_ERROR_NOT_RESPONDING:
            raise USBTC08Error(ret, 'Cannot get a reply from a USB TC-08.')
        elif ret == USBTC08_ERROR_FW_FAIL:
            raise USBTC08Error(ret, 'Unable to download firmware.')
        elif ret == USBTC08_ERROR_CONFIG_FAIL:
            raise USBTC08Error(ret, 'Missing or corrupted EEPROM.')
        elif ret == USBTC08_ERROR_NOT_FOUND:
            raise USBTC08Error(ret, 'Cannot find enumerated device.')
        elif ret == USBTC08_ERROR_THREAD_FAIL:
            raise USBTC08Error(ret, 'A threading function failed.')
        elif ret == USBTC08_ERROR_PIPE_INFO_FAIL:
            raise USBTC08Error(ret, 'Can not get USB pipe information.')
        elif ret == USBTC08_ERROR_NOT_CALIBRATED:
            raise USBTC08Error(ret, 'No calibration date was found.')
        elif ret == USBTC08_ERROR_PICOPP_TOO_OLD:
            raise USBTC08Error(ret, 'An old picopp.sys driver was found on the system.')
        elif ret == USBTC08_ERROR_COMMUNICATION:
            raise USBTC08Error(ret, 'The PC has lost communication with the device.')

    def OpenUnitAsync(self):
        ret = self.__lib.usb_tc08_open_unit_async()
        if ret == 1:
            return
        elif ret == 0:
            raise USBTC08Error(ret, 'No USB TC08 units found')
        elif ret == -1:
            self.GetLastError()
        else:
            raise USBTC08Error(ret, 'Unknown error code %s is detected in OpenUnitAsync')

    def OpenUnitProgress(self):
        self.__handle = ctypes.c_int16()

        while True:
            ret = self.__lib.usb_tc08_open_unit_progress(ctypes.byref(self.__handle), None)

            if ret == USBTC08_PROGRESS_COMPLETE:
                sys.stdout.write('\n')
                break
            elif ret == USBTC08_PROGRESS_FAIL:
                self.GetLastError()
                break
            elif ret == USBTC08_PROGRESS_PENDING:
                sys.stdout.write('|')
                sys.stdout.flush()
                time.sleep(0.2)
                continue
            else:
                raise USBTC08Error(ret, 'Unknown error code was detected in OpenUnitProgress')

        if self.__handle.value <= 0:
            raise USBTC08Error(self.__handle.value, 'No USB TC-08 units found.')

    def GetUnitInfo(self):
        unitInfo = USBTC08Info()
        unitInfo.size = ctypes.sizeof(unitInfo)
        ret = self.__lib.usb_tc08_get_unit_info(self.__handle, ctypes.byref(unitInfo))

        if ret == 1:
            return unitInfo
        elif ret == 0:
            self.GetLastError()
        else:
            raise USBTC08Error(ret, 'Unknown error code %s is detected in GetUnitInfo')

    def SetChannel(self, channel, tc_type):
        ret = self.__lib.usb_tc08_set_channel(self.__handle, ctypes.c_int16(channel), ctypes.c_char(tc_type))
        if ret == 1:
            return
        elif ret == 0:
            self.GetLastError()
        else:
            raise USBTC08Error(ret, 'Unknown error code %s is detected in SetChannel')

    def GetSingle(self, temp, overflow_flags, units):
        ret = self.__lib.usb_tc08_get_single(self.__handle, temp, overflow_flags, ctypes.c_int16(units))
        #ret = self.__lib.usb_tc08_get_single(self.__handle, ctypes.cast(temp, ctypes.POINTER(ctypes.c_float)), 0, ctypes.c_int16(units))
        if ret == 1:
            return
        elif ret == 0:
            self.GetLastError()
        else:
            raise USBTC08Error(ret, 'Unknown error code %s is detected in GetSingle')

    def Close(self):
        ret = self.__lib.usb_tc08_close_unit(self.__handle)
        if ret == 1:
            return
        elif ret == 0:
            self.GetLastError()
        else:
            raise USBTC08Error(ret, 'Unknown error code %s is detected in Close')

if __name__ == '__main__':
    usbtc08 = USBTC08()
    try:
        usbtc08.Open()
    except USBTC08Error as e:
        sys.stderr.write('%s (Error code: %d)\n' % (e.args[1], e.args[0]))
        sys.stderr.write('Error opening unit. Exiting.\n')
        usbtc08.Close()
        sys.exit(-1)
    else:
        sys.stderr.write('USB TC-08 opened successfully.\n')

    try:
        unitInfo = usbtc08.GetUnitInfo()
    except USBTC08Error as e:
        sys.stderr.write('%s (Error code: %d)\n' % (e.args[1], e.args[0]))
        sys.stderr.write('Error getting unit info. Exiting.\n')
        usbtc08.Close()
        sys.exit(-1)
    else:
        print('Unit information:')
        print('Driver: %s \nSerial: %s \nCal date: %s \n' % (unitInfo.DriverVersion.decode(), unitInfo.szSerial.decode(), unitInfo.szCalDate.decode()))

    try:
        usbtc08.SetChannel(USBTC08_CHANNEL_CJC, b'C')
    except USBTC08Error as e:
        sys.stderr.write('%s (Error code: %d)\n' % (e.args[1], e.args[0]))
        sys.stderr.write('Error in cold junction compensentation. Exiting.\n')
        usbtc08.Close()
        sys.exit(-1)

    for i, ch in enumerate((USBTC08_CHANNEL_1, USBTC08_CHANNEL_2, USBTC08_CHANNEL_3, USBTC08_CHANNEL_4,
                            USBTC08_CHANNEL_5, USBTC08_CHANNEL_6, USBTC08_CHANNEL_7, USBTC08_CHANNEL_8)):
        try:
            usbtc08.SetChannel(ch, b'K') # type K thermocouple
        except USBTC08Error as e:
            sys.stderr.write('%s (Error code: %d)\n' % (e.args[1], e.args[0]))
            sys.stderr.write('Error in setting channel %d. Exiting.\n' % i)
            usbtc08.Close()
            sys.exit(-1)

    temp = (ctypes.c_float*(USBTC08_MAX_CHANNELS + 1))()
    try:
        overflow_flags = (ctypes.c_int16*(USBTC08_MAX_CHANNELS + 1))()
        units = USBTC08_UNITS_CENTIGRADE
        usbtc08.GetSingle(temp, overflow_flags, units)
        print('CJC      : %3.2f C' % temp[0])
        for i, ch in enumerate((USBTC08_CHANNEL_1, USBTC08_CHANNEL_2, USBTC08_CHANNEL_3, USBTC08_CHANNEL_4,\
                                USBTC08_CHANNEL_5, USBTC08_CHANNEL_6, USBTC08_CHANNEL_7, USBTC08_CHANNEL_8)):
            print('Channel %d: %3.2f C' % (i, temp[ch]))

    except USBTC08Error as e:
        sys.stderr.write('%s (Error code: %d)\n' % (e.args[1], e.args[0]))
        sys.stderr.write('Error in closing unit. Exiting.\n')
        sys.exit(-1)

    try:
        usbtc08.Close()
    except USBTC08Error as e:
        sys.stderr.write('%s (Error code: %d)\n' % (e.args[1], e.args[0]))
        sys.stderr.write('Error in closing unit. Exiting.\n')
        sys.exit(-1)
