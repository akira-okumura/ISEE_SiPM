import visa,time,gzip,os




##def savewaveform(file0, file1, file2, lecroy):
##    delim = b'***'            # 0704 add b
##    # force trigger here "FORCE_TRIGGER" ???
##    lecroy.write("TRMD SINGLE")
##    time.sleep(0.1)
##
##    for filename, ch in ((file0, 1), (file1, 2), (file2, 3)):
##        lecroy.write("C%d:INSPECT? 'WAVEDESC'; WAVEFORM? DAT1" % ch)    # 0704 delete "c1;"
##        time.sleep(0.1)
##        data = lecroy.read_raw()
##        time.sleep(0.1)
##
##        if data[-1] == '\n':
##            waveform = data[:-1]
##        else:waveform = data    # 0704 delete "=" syntax error
##
##        filename.write(waveform + delim)
##    wavefom = None
##    del(waveform)

def savewaveform(file0, file1, mso):
    '''
    waveform = mso.getWaveform()
    delim = '***'
    file.write(waveform + delim)
    waveform = None
    del(waveform)
    '''

    delim = b"***"
    for filename, ch in ((file0, 1), (file1, 2)):
        mso.write("DATa:SOUrce CH%d"%ch)
        mso.write("WAVFrm?")
        data = mso.read_raw()

        if data[-1] == '\n':
            waveform = data[:-1]
        else:waveform = data

        filename.write(waveform + delim)
    wavefom = None
    del(waveform)

def readout(fname, Nforms, dsetname): #in seconds
    start = time.time()
    rm = visa.ResourceManager()
    mso = rm.open_resource('TCPIP0::192.168.1.1::inst0::INSTR')

    mso.write('WFMInpre:BYT_Nr 2')
    mso.write('WFMOutpre:BYT_Nr 2')

    #ang = -15
    dirname = '%s'%dsetname
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    fil0 = gzip.open("%s/ch1_%s.txt.gz" %(dirname, fname),"wb",6)
    fil1 = gzip.open("%s/ch2_%s.txt.gz" %(dirname, fname),"wb",6)

    #Nevents = 24
 #   Nforms = 4
    for i in range(Nforms):
        savewaveform(fil0, fil1, mso)
        print('read %s/%s'%(i+1,Nforms))


    fil0.close()
    fil1.close()
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
