#   '$Name:  $pp`';
#   '$Header:  $';
#=============================================================================
#
# file :       PyDsJulabo.py 
#
# description : The device server is to communicate with the Julabo Devices
#               Using the Serial Line Communication.  
#
# project :     TANGO Device Server
#
# $Author:  $
#
# $Revision:  $
#
# $Log:  $
#
# copyleft :    Alba Synchrotron Radiation Facility
#               Cerdanyola del Valles
#               Spain
#
#
#         (c) - Controls group - ALBA
#=============================================================================

import PyTango
import sys
import time
from JulaboLib import Julabo 






class PyDsJulaboClass(PyTango.DeviceClass):

    class_property_list = {
        }

    #   Device Properties
    device_property_list = {
        'port':[PyTango.DevString, 'Serial port name', '/dev/ttyS0' ],  
        'baudrate': [PyTango.DevLong, 'Serial port bautrate', 9600 ],
        }

    #   Command definitions
    
    #TODO:
    #Create commands to Start and Stop the Device Remotely
    cmd_list = {}
   
    attr_list = {
                  #'useWorkingTemperatureSP1':[[PyTango.ArgType.DevDouble, 
                  #            PyTango.AttrDataFormat.SCALAR,
                  #            PyTango.AttrWriteType.READ]],
                  'setPoint1':[[PyTango.ArgType.DevString, 
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ_WRITE]],
                  'pumpPressureStage':[[PyTango.ArgType.DevString, 
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ_WRITE]],
                  'bathTemp':[[PyTango.ArgType.DevString, 
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ]],
                  'heatingPower':[[PyTango.ArgType.DevString, 
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ]],
                  'extSensorTemp':[[PyTango.ArgType.DevString, 
                              PyTango.AttrDataFormat.SCALAR,
                              PyTango.AttrWriteType.READ]],

                 }
    
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type("PyDsJulabo")
        
class PyDsJulabo(PyTango.Device_4Impl):

    #@PyTango.DebugIt()
    def __init__(self,cl,name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        self.info_stream('In PyDsJulabo.__init__')
        PyDsJulabo.init_device(self)

    @PyTango.DebugIt()
    def init_device(self):
        self.info_stream('In Python init_device method')
        self.get_device_properties(self.get_device_class())
        self.julabo_device = Julabo(port=self.port, baudrate=self.baudrate)

    #------------------------------------------------------------------

    @PyTango.DebugIt()
    def delete_device(self):
        self.info_stream('PyDsJulabo.delete_device')
        self.julabo_device._close()
        
        
        
    #------------------------------------------------------------------
    # ATTRIBUTES
    #------------------------------------------------------------------

    @PyTango.DebugIt()
    def read_setPoint1(self, the_att):
        self.info_stream("read_setPoint1")
        sp = self.julabo_device.SetPoint1
        the_att.set_value(sp)

    @PyTango.DebugIt()
    def write_setPoint1(self, the_att):
        self.info_stream("write_setPoint1")  
	self.julabo_device.SetPoint1 = the_att.get_write_value()
        
    @PyTango.DebugIt()
    def read_pumpPressureStage(self, the_att):
        self.info_stream("read_pumpPressureStage")
        sp = self.julabo_device.PumpPressureStage
        the_att.set_value(sp)
        
    @PyTango.DebugIt()
    def write_pumpPressureStage(self, the_att):
        self.info_stream("write_pumpPressureStage")     
        self.julabo_device.PumpPressureStage = the_att.get_write_value()
        self.setPoint1 = val  
 
    @PyTango.DebugIt()      
    def read_bathTemp(self, the_att):
        self.info_stream("read_bathTemp")
        sp = self.julabo_device.BathTemp
        the_att.set_value(sp)

    @PyTango.DebugIt()        
    def read_heatingPower(self, the_att):
        self.info_stream("read_heatingPower")
        sp = self.julabo_device.HeatingPower
        the_att.set_value(sp)
    
    @PyTango.DebugIt()        
    def read_extSensorTemp(self, the_att):
        self.info_stream("read_extSensorTemp")
        sp = self.julabo_device.ExtSensorTemp
        the_att.set_value(sp)
        
    @PyTango.DebugIt()
    def is_Current_allowed(self, req_type):
        return self.get_state() in (PyTango.DevState.ON,)
        

if __name__ == '__main__':
    util = PyTango.Util(sys.argv)
    util.add_class(PyDsJulaboClass, PyDsJulabo)

    U = PyTango.Util.instance()
    U.server_init()
    U.server_run()
