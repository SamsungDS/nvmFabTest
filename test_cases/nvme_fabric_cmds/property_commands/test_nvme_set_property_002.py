# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send a Property Set command to set Memory Page Size Maximum (MPSMAX)
in the controller capabilities(read-only field).

Verify that the command fails due to read-only block.
'''
import ctypes
import pytest
import sys
import time
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from utils.logging_module import logger
from test_cases.conftest import dummy
from src.macros import *


class TestNVMePropertySet:

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Property Set")
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
        res_status = self.controller.app.submit_admin_passthru(nvme_cmd,
                                                         verify_rsp=True, async_run=False)

        if res_status != 0:
            raise Exception("Property Get failed")
        self.get_property_value = res.value

    def test_property_set_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        nvme_cmd = self.controller.cmdlib.get_property_set_cmd()
        offset = OFFSET_CONTROLLER_CAPABILITIES
        set_value = self.get_property_value | (7 << 52)

        if offset in OFFSETS_64BIT:
            nvme_cmd.cmd.generic_command.cdw10.raw = True
        else:
            nvme_cmd.cmd.generic_command.cdw10.raw = False

        nvme_cmd.cmd.generic_command.cdw11.raw = offset
        nvme_cmd.cmd.generic_command.cdw12.raw = set_value & 0xFFFFFFFF
        nvme_cmd.cmd.generic_command.cdw13.raw = set_value >> 32

        res_status = self.controller.app.submit_admin_passthru(nvme_cmd,
                                                         verify_rsp=True, async_run=False)
        self.controller.app.get_response(nvme_cmd)

        # Verifying Property Set success
        if res_status == 0:
            logger.log("FAIL", "Property Set passed for read-only field")
            assert False, f"Property Set passed for read-only field"
        SC = nvme_cmd.rsp.response.sf.SC
        if SC != 0x82:
            logger.log("FAIL", f"Property Set failed with unexpected status code: {SC}")
            assert False, f"Property Set failed with unexpected status code: {SC}"

        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Property Set")
        logger.info("-"*100)
