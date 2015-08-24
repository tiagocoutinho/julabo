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
from JulaboLib import Julabo



class PyDsJulaboClass(PyTango.DeviceClass):

    class_property_list = {
        }

    #   Device Properties
    device_property_list = {
        'model': [PyTango.DevString, 'Julabos Model', 'CF41'],
        'port': [PyTango.DevString, 'Serial port name', '/dev/ttyS0'],
        'baudrate': [PyTango.DevLong, 'Serial port bautrate', 9600],
        }

    cmd_list = {'Start': [[PyTango.ArgType.DevVoid, ""],
                              [PyTango.ArgType.DevVoid, ""]],
                'Stop': [[PyTango.ArgType.DevVoid, ""],
                              [PyTango.ArgType.DevVoid, ""]],

                }
   
    attr_list = {

                  'JulaboStatus':[[PyTango.ArgType.DevString, 
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
        self.model = self.model.lower()
        self.julabo_device = Julabo(port=self.port, baudrate=self.baudrate, 
                                    model=self.model)

        self.configuration = self.julabo_device.getDevConfiguration()
        self.dyn_attr()

    def dyn_attr(self):

        self.attr_to_use = self.configuration['attributes']

        for attr in self.attr_to_use:
            attr_name = attr
            attr = self.attr_to_use[attr]

            attr_type = PyTango.AttrWriteType.READ
            writable = attr.has_key('write')
            write_method = None

            if writable:
                write_method = self.write_dyn_attr
                attr_type = PyTango.AttrWriteType.READ_WRITE
                
            attrib = PyTango.Attr(attr_name, PyTango.DevString, attr_type)
            self.add_attribute(attrib, self.read_dyn_attr, write_method,
                               is_allo_meth=None)

    def dyn_cmd(self):
        self.cmds_to_use = self.configuration['commands']
        for cmd in self.cmds_to_use:
            command_name = cmd
            cmd = self.cmds_to_use[cmd]


    #------------------------------------------------------------------


    @PyTango.DebugIt()
    def delete_device(self):
        self.info_stream('PyDsJulabo.delete_device')
        self.julabo_device._close()
        
    def read_dyn_attr(self,attr):
        attrname = attr.get_name()
        self.info_stream('In read_dyn_attr(%s)'%attrname)
        cmd = self.attr_to_use[attrname]['read']
        response = self.julabo_device._sendCmdWaitResponse(cmd)
        attr.set_value(response)
    
    def write_dyn_attr(self, attr):
        attrname = attr.get_name()
        val = str(attr.get_write_value())
        self.info_stream('In write_dyn_attr(%s) with value(%s)'%(attrname, val))
        cmd = self.attr_to_use[attrname]['write']
        cmd = cmd + ' ' + str(val)
        self.julabo_device._sendCmd(cmd)

    #------------------------------------------------------------------
    # Commands
    #------------------------------------------------------------------

    def Start(self):
        self.info_stream('In Start Command(%s)')
        self.julabo_device.start()

    def Stop(self):
        self.info_stream('In Stop Command(%s)')
        self.julabo_device.stop()

    #------------------------------------------------------------------
    # ATTRIBUTES
    #------------------------------------------------------------------

    @PyTango.DebugIt()
    def read_JulaboStatus(self, the_att):
        self.info_stream("read_JulaboStatus")
        sp = self.julabo_device.JulaboStatus
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
