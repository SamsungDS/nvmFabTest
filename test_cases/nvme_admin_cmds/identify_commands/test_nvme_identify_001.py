'''
Sends Identify Controller Command and verifies that the Serial Number has 
characters in the range of 20h to 7Eh in Identify Response Data Structure
'''

from src.macros import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import Controller
import ctypes
import pytest


class TestNVMeIdentify:
    '''
    Sends Identify Controller Command and verifies that the Serial Number has 
    characters in the range of 20h to 7Eh in Identify Response Data Structure
    '''

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
        nvme_cmd = self.controller.cmdlib.get_identify_controller_cmd()

        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)

        res_status = self.controller.app.submit_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            assert False, f"Identify failed: {res_status}"

        self.controller.app.get_response(nvme_cmd)
        print("Status Code: ", nvme_cmd.rsp.response.sf.SC)

        SN = result.SN.decode().strip()
        for char in SN:
            if not ASCII_MIN <= ord(char) < ASCII_MAX:
                assert False, f"ASCII out of range: {ord(char)}"
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        print("Teardown TestCase: Identify Controller")
        print("-"*100)
