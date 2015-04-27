import serial
import logging
import re


CMDS = {
        #{'useWorkingTemperatureSP1':
        #    {'read': 'out_mode_01'}},
        {'setPoint':
            {'read': 'in_sp_00', 'write': 'out_sp_00'}},
        {'pumpPressureStage':
            {'read': 'in_sp_07', 'write':'out_sp_07'}}, 
        {'bathTemp': 
            {'read': 'in_pv_00'}},
        {'heatingPower':
            {'read': 'in_pv_01'}}, 
        {'extSensorTemp':
            {'read': 'in_pv_02'}}
        }


class Julabo(object):
    
    def __init__(self, port='/dev/ttyR14', baudrate=9600,   # baud rate
                 bytesize=serial.SEVENBITS,    # number of data bits
                 parity=serial.PARITY_EVEN,    # enable parity checking
                 stopbits=serial.STOPBITS_ONE, # number of stop bits
                 timeout=3,          # set a timeout value, None to wait forever
                 rtscts=True,  ):
       
        self._comm = serial.Serial(port, baudrate=baudrate, bytesize=bytesize,
                                 parity=parity, stopbits=stopbits, 
                                 timeout=timeout, rtscts=rtscts)
        logging.debug('Created Julabo object') 
        self._open()
    
    def _read(self):
        try:
            logging.debug('Reading response')
            result = self._comm.readline()
            logging.debug('Read %s Value', repr(result))
            result = self._getValueFromResponse(result)
        except Exception, e:
            result = None
        return result

    def _write(self, data):
        
        try:
            logging.debug('Writing command')
            data = data + '\n'
            self._comm.write(data)
        except Exception, e:
            return False
        return True

    def _sendCmdWaitResponse(self, cmd):
        
        logging.debug('Sending %s command with response', cmd)
        if self._write(cmd):
            return self._read()
        return None
    
    def _sendCmd(self, cmd):
        
        logging.debug('Sending %s command', cmd)
        self._write(cmd)
        
    def _open(self):
        
        logging.debug('Opening Port')
        self._comm.open()
            
    def _close(self):
        
        logging.debug('Closing Port')
        self._comm.close()
                 
    def __exit__(self):
        
        self._close()
        
    def __del__(self):
        
        self._close()
        
    @property
    def SetPoint1(self, val):
        cmd = self.CMDS['setPoint1']['write']
        cmd = cmd + ' '+val
        self._sendCmd(cmd)
        
    @property
    def SetPoint1(self):
        cmd = self.CMDS['setPoint1']['read']
        return self._sendCmdWaitResponse(cmd)
    
    @property
    def umpPressureStage(self,val):
        cmd = self.CMDS['pumpPressureStage']['write']
        cmd = cmd + ' '+val
        self._sendCmd(cmd)
        
    @property    
    def umpPressureStage(self):
        cmd = self.CMDS['pumpPressureStage']['read']
        return self._sendCmdWaitResponse(cmd)

    def getBathTemp(self):
        cmd = self.CMDS['bathTemp']['read']
        return self._sendCmdWaitResponse(cmd)

    def getHeatingPower(self):
        cmd = self.CMDS['heatingPower']['read']
        return self._sendCmdWaitResponse(cmd)
    
    def getExtSensorTemp(self):
        cmd = self.CMDS['extSensorTemp']['read']
        return self._sendCmdWaitResponse(cmd)

        
    
        
    def _getValueFromResponse(self,data):
        
        data = (re.findall("\d+.\d+",data))[0]
        logging.debug('Cleaned response:  %s ', data)
        
        return data    
        
            
if __name__ == '__main__':
    format ='%(asctime)s %(levelname)s:%(message)s'
    level = logging.DEBUG
    logging.basicConfig(format=format,level=level)
    
    cmd_test= 'in_sp_00'
    a = Julabo()
    r = a.sendCmd(cmd_test)
    a._getValueFromResponse(r)

    