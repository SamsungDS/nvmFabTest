# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send a Property Get command (FCTYPE=04h) with the following reserved
offset value:
0Ch-0Fh INTMS
10h-13h INTMC
18h-1Bh Reserved
24h-27h AQA
28h-2Fh ASQ
30h-37h ACQ
38h-3Bh CMBLOC
3Ch-3Fh CMBSZ
40h-EFFh Reserved
F00h-FFFh Reserved
1000h-12FFh Reserved

Verify that the Property Get commands completed with status “Success”
and all values returned were 0h
'''
import ctypes
import pytest
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from utils.logging_module import logger
from test_cases.conftest import dummy
from src.macros import *


class TestNVMePropertyGet:

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n", "-"*100)
        logger.info("Setup TestCase: Property Get")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_property_get_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        nvme_cmd = self.controller.cmdlib.get_property_get_cmd()
        offsets = [0x0C, 0x10, 0x18, 0x24, 0x28,
                   0x30, 0x38, 0x3C, 0x40, 0xF00, 0x1000]
        fail = []
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

            # self.controller.app.get_response(nvme_cmd)
            if res_status != 0:
                fail.append(offset)

            get_property_hex_value = hex(get_property_value.value)

            if get_property_value.value != 0:
                fail.append(offset)
                logger.log("FAIL", f"Value obtained {get_property_hex_value} but expected 0")
                assert False, f"Value obtained {get_property_hex_value} but expected 0"

        if len(fail) != 0:
            passed = [a for a in offsets if a not in fail]
            logger.log("FAIL", f"Failed for offsets: {fail}\nPassed for offsets {passed}")
            assert False, f"Failed for offsets: {fail}\nPassed for offsets {passed}"
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Property Get")
        logger.info("-"*100)
