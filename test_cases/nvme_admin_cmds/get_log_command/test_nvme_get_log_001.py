'''
Sends Get Log Command and verifies that the Serial Number has 
characters in the range of 20h to 7Eh in GetLog Response Data Structure
'''

from src.macros import *
from test_cases.conftest import dummy
from lib.devlib.device_lib import Controller
import ctypes
import pytest


class TestNVMeGetLog:
    '''
    Send Get Log Command to retrieve Firmware Slot information.
    Check the Active Slot Number and verify that the firmware revision
    in that slot is not cleared to 0h
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        print("\n", "-"*100)
        print("Setup TestCase: Get Log")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_get_log_cmd(self, dummy):
        ''' Sending the command and verifying response '''
        
        log_id = 3
        log_len = 64
        
        nvme_cmd = self.controller.cmdlib.get_get_log_cmd(log_id, log_len)

        result = ctypes.create_string_buffer(log_len)
        nvme_cmd.buff = ctypes.addressof(result)
        
        res_status = self.controller.app.submit_passthru(
            nvme_cmd, verify_rsp=True, async_run=False) 
        if res_status != 0:
            assert False, f"Get Log failed: {res_status}"

        self.controller.app.get_response(nvme_cmd)
        print("Status Code: ", nvme_cmd.rsp.response.sf.SC)

        slot_number = result.raw[0]
        if not 0 < slot_number < 8:
            assert False, "Invalid Slot number"
        
        l = slot_number * 8
        r = l + 8

        fw = result.raw[l:r].decode()
        for char in fw:
            if not ASCII_MIN <= ord(char) < ASCII_MAX:
                assert False, f"ASCII out of range: {int(char)}"
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        print("Teardown TestCase: Get Log")
        print("-"*100)
