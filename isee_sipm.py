import gzip, struct, enum, ROOT
import numpy as np
from concurrent.futures import ProcessPoolExecutor

def gzip2waveforms(raw_data_file_name, nprocess=1):
    '''
    Convert a gzipped raw data file into SiPMWaveform instances. Here we assume
    individual waveforms are separated by '***'.
    '''
    try:
        f = gzip.open(raw_data_file_name)
        raw_data = f.read()
    except OSError as e:
        if e.args[0].find('Not a gzipped file') == 0:
            f = open(raw_data_file_name)
            raw_data = f.read()
    raw_data_list = raw_data.split(b'***')[:-1] # Assume here that *** is used as data splitter
    if nprocess > 1:
        executor = ProcessPoolExecutor(max_workers = nprocess)
        futures = [executor.submit(SiPMWaveform, rd) for rd in raw_data_list]
        waveform_list = [f.result() for f in futures]
    else:
        waveform_list = [SiPMWaveform(rd) for rd in raw_data_list]
    
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
        elif len(raw_data.split(b';')) == 17:
            self.instrument = InstrumentType.TEKTRONIX
            self.decode_tektronix_raw_data(raw_data)
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
        self.yarray = np.array(struct.unpack('>' + 'h' * Npt, wave_byte))

        # scale y and add offset
        vscale = self.get_vscale()
        voffset = self.get_voffset()
        self.yarray = vscale * self.yarray - voffset

        # set x array
        dt = self.get_dt()
        self.xarray = np.linspace(0, dt*(Npt - 1), Npt)

    def decode_tektronix_raw_data(self, raw_data):
        self.header = raw_data.split(b';')[:16]
        byt_nr =   int(header[ 0])
        bit_nr =   int(header[ 1])
        encdg  =       header[ 2]
        bn_fmt =       header[ 3]
        byt_or =       header[ 4]
        wfid   =       header[ 5]
        nr_pt  =   int(header[ 6])
        pt_fmt =       header[ 7]
        xunit  =       header[ 8]
        #xincr  = float(header[ 9])
        xzero  = float(header[10])
        pt_off =  bool(int(header[11]))
        yunit  =       header[12]
        #ymult  = float(header[13])
        #yoff   = float(header[14])
        #yzero  = float(header[15])

        header_length = 0
        for i in range(16):
            header_length += len(header[i]) + 1
            raw_data = raw_data[header_length:]

        if raw_data[0] == '#':
            # binary data
            x = int(raw_data[1])
            yyy = int(raw_data[2:2 + x])
            if yyy != byt_nr*nr_pt:
                raise RuntimeError('NR_PT (numbr of point) is invalid.')
            if len(raw_data[2 + x:]) > byt_nr*nr_pt:
                raise RuntimeError('Received data length is too long.')
            elif len(raw_data[2 + x:]) < byt_nr*nr_pt:
                raise RuntimeError('Received data length is too short.')

            # RI means signed integer
            # RP means positive (unsigned) integer
            # MSB means the MSB is transmitted first
            # LSB means the LSB is transmitted first
            format = ''
            if byt_or == 'MSB':
                format += '>'
            elif byt_or == 'LSB':
                format += '<'
            else:
                raise RuntimeError('Invalid BYT_OR (%s)' % byt_or)

            if bn_fmt == 'RI' and byt_nr == 1:
                # signed char
                format += 'b'*nr_pt
            elif bn_fmt == 'RI' and byt_nr == 2:
                # signed short
                format += 'h'*nr_pt
            elif bn_fmt == 'RP' and byt_nr == 1:
                # unsigned char
                format += 'B'*nr_pt
            elif bn_fmt == 'RP' and byt_nr == 2:
                # unsigned char
                format += 'H'*nr_pt
            else:
                raise RuntimeError('Invalid binary format BN_FMT(%s) BYT_NR(%d).' % (bn_fmt, byt_nr))
            sefl.yarray = numpy.array(struct.unpack(format, raw_data[2 + x:])) * self.get_vscale() + yzero - self.get_voffset()
        else:
            # ASCII data
            pass

        self.xarray = (numpy.arange(nr_pt) - pt_off) * self.get_dt() + xzero

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
        elif self.instrument == InstrumentType.TEKTRONIX:
            return float(self.header[9])
        else:
            raise 'Not implemented yet'

    def get_dv(self):
        if self.instrument == InstrumentType.LE_CROY:
            return float(self.header[b'VERTICAL_GAIN']) * 2 ** (16 - int(self.header[b'NOMINAL_BITS']))
        elif self.instrument == InstrumentType.TEKTRONIX:
            return self.get_vscale()
        else:
            raise 'Not implemented yet'

    def get_vscale(self):
        if self.instrument == InstrumentType.LE_CROY:
            return float(self.header[b'VERTICAL_GAIN'])
        elif self.instrument == InstrumentType.TEKTRONIX:
            return float(self.header[13])
        else:
            raise 'Not implemented yet'

    def get_voffset(self):
        if self.instrument == InstrumentType.LE_CROY:
            return float(self.header[b'VERTICAL_OFFSET'])
        elif self.instrument == InstrumentType.TEKTRONIX:
            return float(self.header[14]) * self.get_vscale()
        else:
            raise 'Not implemented yet'

    def get_n(self):
        return len(self.xarray)
