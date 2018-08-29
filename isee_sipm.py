import gzip, struct, enum, ROOT
import numpy as np

def gzip2waveforms(raw_data_file_name):
    try:
        f = gzip.open(raw_data_file_name)
        raw_data = f.read()
    except OSError as e:
        if e.args[0].find('Not a gzipped file') == 0:
            f = open(raw_data_file_name)
            raw_data = f.read()

    raw_data_list = raw_data.split(b'***')[:-1] # Assume here that *** is used as data splitter
    waveform_list = []
    for rd in raw_data_list:
        waveform_list.append(SiPMWaveform(rd))

    return waveform_list

class InstrumentType(enum.Enum):
    TEKTRONIX = 0
    LE_CROY = 1
    TARGET7 = 2

class SiPMWaveform:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.decode_raw_data(raw_data)

    def decode_raw_data(self, raw_data):
        if raw_data.find(b'\r\n";') >= 0:
            self.instrument = InstrumentType.LE_CROY
            self.decode_lecroy_raw_data(raw_data)
        else:
            # Write other functions for TARGET modules and Tektronix
            raise 'Not implemented yet'

    def decode_lecroy_raw_data(self, raw_data):
        """
        input : lecroy rawdata
                acquired by command "INSPECT? 'WAVEDESC';c1:WAVEFORM? DAT1"
        output : x(numpy array,y(numpy array), header_info (dictionary)
        """
        header_raw, waveform_raw = raw_data.split(b'\r\n";')

        # convert header data to dictionary
        self.header = {}
        for readline in header_raw.split(b'\n'):
            if b':' in readline:
                if readline.count(b':') == 1:  # "<key>:<value>"
                    key, value = readline.split(b':')
                    self.header[key.replace(b' ', b'')] = value.replace(b' ', b'').replace(b'\r', b'')
                else:  # ex. "... Time =  4:51:11..."
                    key, value = readline.split(b': D') # add D "Time =  4: 5:10"
                    self.header[key.replace(b' ', b'')] = b'D' + value.replace(b' ', b'')

        Npt = int(self.header[b'WAVE_ARRAY_COUNT'])
        
        Nbyte = Npt * 2  # 16-bit
        wave_byte = waveform_raw[-Nbyte:]  # data segment

        # unpack raw wavedata
        # 16-bit signed integar (h) with lofirst order (>)
        self.yarray = 1.0 * np.array(struct.unpack('>' + 'h' * Npt, wave_byte))

        # scale y and add offset
        vscale = self.get_vscale()
        voffset = self.get_voffset()
        self.yarray = vscale * self.yarray - voffset

        # set x array
        dt = self.get_dt()
        self.xarray = dt * np.arange(Npt)

    def decode_tektronix_raw_data(self, raw_data):
        pass

    def decode_target_raw_data(self, raw_data):
        pass

    def filter_moving_average(self, n):
        """
        Calculate movinge average of waveform by using numpy.convolve
        https://docs.scipy.org/doc/numpy/reference/generated/numpy.convolve.html
        """
        weight = np.ones(n) / n
        return np.convolve(self.yarray, weight, 'same')

    def get_dt(self):
        if self.instrument == InstrumentType.LE_CROY:
            return float(self.header[b'HORIZ_INTERVAL'])
        else:
            raise 'Not implemented yet'

    def get_dv(self):
        if self.instrument == InstrumentType.LE_CROY:
            return float(self.header[b'VERTICAL_GAIN']) * 2 ** (16 - int(self.header[b'NOMINAL_BITS']))
        else:
            raise 'Not implemented yet'

    def get_vscale(self):
        if self.instrument == InstrumentType.LE_CROY:
            return float(self.header[b'VERTICAL_GAIN'])
        else:
            raise 'Not implemented yet'

    def get_voffset(self):
        if self.instrument == InstrumentType.LE_CROY:
            return float(self.header[b'VERTICAL_OFFSET'])
        else:
            raise 'Not implemented yet'

    def get_n(self):
        return len(self.xarray)
