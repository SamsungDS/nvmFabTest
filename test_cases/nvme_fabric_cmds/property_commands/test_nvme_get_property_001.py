'''
Sends Property Get Command for all offsets and verify that
non-zero response is obtained.
'''
import ctypes
import pytest
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from test_cases.conftest import dummy
from src.macros import *


class TestNVMePropertyGet:
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        print("\n", "-"*100)
        print("Setup TestCase: Identify Controller")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_property_get_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        nvme_cmd = self.controller.cmdlib.get_property_get_cmd()
        offsets =  [0, 0x08, 0x14, 0x1C]
        
        for offset in offsets:
            get_property_value = ctypes.c_uint64()
            nvme_cmd.buff = ctypes.addressof(get_property_value)
            nvme_cmd.cmd.generic_command.cdw11.raw = offset
            if offset in OFFSETS_64BIT:
                nvme_cmd.cmd.generic_command.cdw10.raw = True
            else:
                nvme_cmd.cmd.generic_command.cdw10.raw = False
            res_status = self.controller.app.submit_passthru(nvme_cmd,
                                                              verify_rsp=True, async_run=False)
            
            
            if res_status!=0:
                assert False, f"Command failed with status code: {res_status}"
            get_property_hex_value = hex(get_property_value.value)
            print(get_property_hex_value)
            if get_property_value.value == 0:
                assert False, f"No value obtained"
            assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        print("Teardown TestCase: Identify Controller")
        print("-"*100)
