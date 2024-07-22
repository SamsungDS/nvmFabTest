# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Sends Identify Controller Command and verifies that the Serial Number has 
characters in the range of 20h to 7Eh in Identify Response Data Structure
'''

import ctypes
import pytest
from src.macros import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from utils.logging_module import logger
from lib.devlib.device_lib import Controller


class TestNVMeIdentify:
    '''
    Sends Identify Controller Command and verifies that the Serial Number has 
    characters in the range of 20h to 7Eh in Identify Response Data Structure
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n"+ "-"*100)
        logger.info("Setup TestCase: Identify Controller")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_identify_cmd(self, dummy):
        ''' Sending the command and verifying response '''
        nvme_cmd = self.controller.cmdlib.get_identify_controller_cmd()

        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)

        res_status = self.controller.app.submit_admin_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            assert False, f"Identify failed: {res_status}"

        self.controller.app.get_response(nvme_cmd)
        logger.info("Status Code: {}", nvme_cmd.rsp.response.sf.SC)

        SN = result.SN.decode().strip()
        for char in SN:
            if not ASCII_MIN <= ord(char) < ASCII_MAX:
                logger.log("FAIL", f"ASCII out of range: {ord(char)}")
                assert False, f"ASCII out of range: {ord(char)}"
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Identify Controller")
        logger.info("-"*100)
