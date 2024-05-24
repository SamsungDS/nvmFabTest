'''
Send a Property Set command to set Arbitration Mechanism Selected (AMS)
in the controller capabilities.

Verify that the command fails if CC.EN is 1, and command passes if
CC.EN is 0.
'''
import ctypes
import pytest,sys
import time
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from test_cases.conftest import dummy
from src.macros import *


class TestNVMePropertySet:
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        print("\n", "-"*100)
        print("Setup TestCase: Identify Controller")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)
        
        nvme_cmd = self.controller.cmdlib.get_property_get_cmd()
        offset = OFFSET_CONTROLLER_CONFIGURATION
        res = ctypes.c_uint64()
        nvme_cmd.buff = ctypes.addressof(res)
        nvme_cmd.cmd.generic_command.cdw11.raw = offset
        if offset in OFFSETS_64BIT:
            nvme_cmd.cmd.generic_command.cdw10.raw = True
        else:
            nvme_cmd.cmd.generic_command.cdw10.raw = False
        res_status = self.controller.app.submit_passthru(nvme_cmd,
                                                            verify_rsp=True, async_run=False)
        if res_status!=0:
            raise Exception("Property Get failed")
        self.get_property_value = res.value

    def test_property_set_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        nvme_cmd = self.controller.cmdlib.get_property_set_cmd()

        offset = OFFSET_CONTROLLER_CAPABILITIES

        set_value = self.get_property_value | (1 << 11)
        cc_en = self.get_property_value % 2
        if offset in OFFSETS_64BIT:
            nvme_cmd.cmd.generic_command.cdw10.raw = True
        else:
            nvme_cmd.cmd.generic_command.cdw10.raw = False
        
        nvme_cmd.cmd.generic_command.cdw11.raw = offset
        nvme_cmd.cmd.generic_command.cdw12.raw = set_value & 0xFFFFFFFF
        nvme_cmd.cmd.generic_command.cdw13.raw = set_value >> 32
        
        res_status = self.controller.app.submit_passthru(nvme_cmd,
                                                            verify_rsp=True, async_run=False)
        # Verifying Property Set success
        if res_status==0 and cc_en==1:
            assert False, f"Property Set passed for CC.AMS when CC.EN is 1"

        if res_status!=0 and cc_en==0:
            assert False, f"Property Set failed for CC.AMS when CC.EN is 0"
    
        # time.sleep(0) # Use if want to wait before checking 
        
        # # Verifying Shutdown success by checking if fabric command passes
        # nvme_cmd = self.controller.cmdlib.get_property_get_cmd()
        # res_status = self.controller.app.submit_passthru(
        #     nvme_cmd, verify_rsp=True, async_run=False)
        # if res_status != 0:
        #     assert False, "Fabric command failed after Shutdown Notification"
        
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        print("Teardown TestCase: Identify Controller")
        print("-"*100)   
