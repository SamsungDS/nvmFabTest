'''
Send Get Log Command to retrieve Firmware Slot information.
Check the Active Slot Number and verify that the firmware revision
in that slot is not cleared to 0h
'''

import ctypes
import pytest
from src.macros import *
from test_cases.conftest import dummy
from utils.logging_module import logger
from lib.devlib.device_lib import Controller


class TestNVMeGetLog:
    '''
    Send Get Log Command to retrieve Firmware Slot information.
    Check the Active Slot Number and verify that the firmware revision
    in that slot is not cleared to 0h
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n", "-"*100)
        logger.info("Setup TestCase: Get Log")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_get_log_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        log_id = 3
        log_len = 64

        nvme_cmd = self.controller.cmdlib.get_get_log_cmd(log_id, log_len)

        data = ctypes.create_string_buffer(log_len)
        nvme_cmd.buff = ctypes.addressof(data)

        res_status = self.controller.app.submit_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            self.controller.app.get_response(nvme_cmd)
            logger.log("FAIL", "Status Code: {}", nvme_cmd.rsp.response.sf.SC)
            assert False, f"Get Log failed: {res_status}"

        slot_number = data.raw[0]
        if not 0 < slot_number < 8:
            logger.log("FAIL", "Invalid Slot number")
            assert False, "Invalid Slot number"

        l = slot_number * 8
        r = l + 8

        fw = data.raw[l:r].decode()
        for char in fw:
            if not ASCII_MIN <= ord(char) < ASCII_MAX:
                logger.log("FAIL", f"ASCII out of range: {ord(char)}")
                assert False, f"ASCII out of range: {ord(char)}"
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Get Log")
        logger.info("-"*100)
