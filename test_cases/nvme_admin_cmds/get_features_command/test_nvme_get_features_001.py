# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Sends Get Features Command to retrieve the number of submission and completion queues.
Verify command executed successfully
'''

import ctypes
import pytest
from src.macros import *
from test_cases.conftest import fabConfig
from utils.logging_module import logger
from lib.devlib.device_lib import Controller


class TestNVMeGetFeatures:
    '''
    Sends Get Features Command to retrieve the number of submission and completion queues.
    Verify command executed successfully
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, fabConfig):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Get Features")
        self.fabConfig = fabConfig
        device = self.fabConfig.device
        application = self.fabConfig.application
        self.controller = Controller(device, application)
        logger.info("Completed Setup\n\n")

    def test_get_features_cmd(self, fabConfig):
        ''' Sending the command and verifying response '''

        features_id = 7
        nvme_cmd = self.controller.cmdlib.get_get_features_cmd(features_id)

        res_status = self.controller.app.submit_admin_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            self.controller.app.get_response(nvme_cmd)
            logger.log("FAIL", "Status Code: {}", nvme_cmd.rsp.response.sf.SC)
            assert False, f"Get Features failed: {res_status}"

        result = self.controller.app.get_passthru_result()

        result = int(result, 16)
        n_cq = result >> 16
        n_sq = result & 0xFFFF
        logger.info("-- Number of Submission Queues: {}", n_sq)
        logger.info("-- Number of Completion Queues: {}", n_cq)

        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("\n\nTeardown TestCase: Get Features")
        logger.info("Completed Teardown")
        logger.info("-"*100)
