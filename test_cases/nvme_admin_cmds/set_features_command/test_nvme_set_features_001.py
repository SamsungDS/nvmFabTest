# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send a Set Features Command to set TLER field of Error Recovery (feature-id 5)
to 3000ms.
Verify the value is set using Get Feature command.
'''

import ctypes
import pytest
from src.macros import *
from test_cases.conftest import dummy
from utils.logging_module import logger
from lib.devlib.device_lib import Controller


class TestNVMeSetFeatures:
    '''
    Send a Set Features Command to set TLER field of Error Recovery (feature-id 5)
    to 3000ms.
    Verify the value is set using Get Feature command.
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Set Features")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)
        logger.info("Completed Setup\n\n")

    def test_set_features_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        features_id = 5
        feature_value = 30 # 30*100 ms
        nvme_cmd = self.controller.cmdlib.get_set_features_cmd(features_id)

        nvme_cmd.cmd.generic_command.cdw11.raw = feature_value & ((1<<16) - 1)
        
        res_status = self.controller.app.submit_admin_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            self.controller.app.get_response(nvme_cmd)
            logger.log("FAIL", "Status Code: {}", nvme_cmd.rsp.response.sf.SC)
            assert False, f"Set Features failed: {res_status}"

        result = self.controller.app.get_passthru_result()

        nvme_cmd = self.controller.cmdlib.get_get_features_cmd(features_id)
        res_status = self.controller.app.submit_admin_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            self.controller.app.get_response(nvme_cmd)
            logger.log("FAIL", "Status Code: {}", nvme_cmd.rsp.response.sf.SC)
            assert False, f"Get Features failed: {res_status}"

        result = self.controller.app.get_passthru_result()

        result = int(result, 16)
        if result == feature_value:
            assert True
        else:
            assert False

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("\n\nTeardown TestCase: Set Features")
        logger.info("Completed Teardown")
        logger.info("-"*100)
