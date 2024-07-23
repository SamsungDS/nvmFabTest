# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Sends Property Get Command for all offsets and verify that
non-zero response is obtained.
'''
import ctypes
import pytest
from utils.logging_module import logger
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
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
        offsets = [0, 0x08, 0x14, 0x1C]

        for offset in offsets:
            get_property_value = ctypes.c_uint64()
            nvme_cmd.buff = ctypes.addressof(get_property_value)
            nvme_cmd.cmd.generic_command.cdw11.raw = offset
            if offset in OFFSETS_64BIT:
                nvme_cmd.cmd.generic_command.cdw10.raw = True
            else:
                nvme_cmd.cmd.generic_command.cdw10.raw = False
            res_status = self.controller.app.submit_admin_passthru(nvme_cmd,
                                                             verify_rsp=True, async_run=False)

            if res_status != 0:
                logger.log("FAIL", f"Command failed with status code: {res_status}")
                assert False, f"Command failed with status code: {res_status}"
            get_property_hex_value = hex(get_property_value.value)
            logger.info(get_property_hex_value)
            if get_property_value.value == 0:
                logger.log("FAIL", "No value obtained")
                assert False, f"No value obtained"
            assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Property Get")
        logger.info("-"*100)
