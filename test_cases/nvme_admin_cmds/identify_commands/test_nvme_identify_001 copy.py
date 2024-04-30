'''
Sends Identify Controller Command and verifies that the Serial Number has 
characters in the range of 20h to 7Eh in Identify Response Data Structure
'''
import sys
import ctypes
import pytest
import re

sys.path.insert(1, "/root/nihal223/nvmfabtest/")
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from test_cases.conftest import dummy
from src.macros import *

class TestNVMeIdentify:
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        print("\n", "-"*100)
        print("Setup TestCase: Identify Controller")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_identify_cmd(self, dummy):
        ''' Sending the command and verifying response '''
        nvme_cmd = self.controller.cmdlib.get_identify_cmd()
        
        # Making it identify-controller command
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0x01

        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)
        res_status = self.controller.submit_passthru_cmd(nvme_cmd, verify_rsp=True, async_run=False)
        
        self.controller.app.get_response(nvme_cmd)
        print("Status Code: ", nvme_cmd.rsp.response.sf.SC)
        if res_status!=0:
            assert False
        SN = result.SN.decode().strip()
        for char in SN:
            if not ASCII_MIN<=ord(char)<ASCII_MAX:
                assert False, f"ASCII out of range: {int(char)}"
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        print("Teardown TestCase: Identify Controller")
        print("-"*100)   
             
from lib.devlib.device_lib import DeviceConfig
print("Hello 0")
if __name__=='__main__':
    print("Hello 1")
    dum = DeviceConfig("/dev/nvme2", "nvme-cli")
    print("Hello 2")
    TestNVMeIdentify().test_identify_cmd(dum)
