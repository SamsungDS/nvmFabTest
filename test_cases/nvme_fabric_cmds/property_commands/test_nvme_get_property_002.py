# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send a Property Get command (FCTYPE=04h) with an invalid offset 
(01h-07h CAP) that is not at the beginning of the property

Verify that the Property Get command fails
'''
import ctypes
import pytest
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from utils.logging_module import logger
from test_cases.conftest import fabConfig
from src.macros import *


class TestNVMePropertyGet:

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, fabConfig):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Property Get")
        self.fabConfig = fabConfig
        device = self.fabConfig.device
        application = self.fabConfig.application
        self.controller = Controller(device, application)

    def test_property_get_cmd(self, fabConfig):
        ''' Sending the command and verifying response '''

        nvme_cmd = self.controller.cmdlib.get_property_get_cmd()

        offset = INVALID_PROPERTY_OFFSET
        get_property_value = ctypes.c_uint64()
        nvme_cmd.buff = ctypes.addressof(get_property_value)
        nvme_cmd.cmd.generic_command.cdw11.raw = offset

        if offset in OFFSETS_64BIT:
            nvme_cmd.cmd.generic_command.cdw10.raw = True
        else:
            nvme_cmd.cmd.generic_command.cdw10.raw = False
        res_status = self.controller.app.submit_admin_passthru(nvme_cmd,
                                                         verify_rsp=True, async_run=False)

        self.controller.app.get_response(nvme_cmd)
        SC = nvme_cmd.rsp.response.sf.SC
        if res_status == 0:
            logger.log("FAIL", "Command passed unexpectedly")
            assert False, "Command passed unexpectedly"
        if SC != 0x2:
            logger.log("FAIL", 
                       f"Command failed with unexpected status code: {hex(SC)}")
            assert False, f"Command failed with unexpected status code: {
                hex(SC)}"

        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Property Get")
        logger.info("-"*100)
