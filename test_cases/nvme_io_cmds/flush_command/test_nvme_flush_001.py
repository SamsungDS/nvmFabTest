# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send an NVM Flush command to NSID 1.
Verify command success.
'''

import ctypes
import pytest
import shutil
from src.macros import *
from test_cases.conftest import fabConfig
from utils.logging_module import logger
from lib.devlib.device_lib import Controller


class TestNVMeFlush:
    '''
    Send an NVM Flush command to NSID 1.
    Verify command success.
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, fabConfig):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n"+"-"*100)
        logger.info("Setup TestCase: Flush")
        self.fabConfig = fabConfig
        device = self.fabConfig.device
        application = self.fabConfig.application
        self.controller = Controller(device, application)

        self.lba_size = self.controller.app.get_device_lba_size()

    def test_flush_cmd(self, fabConfig):
        ''' Sending the command and verifying response '''

        nvme_cmd = self.controller.cmdlib.get_flush_cmd()
        
        res_status = self.controller.app.submit_io_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        
        if res_status != 0:
            assert False, f"Flush failed: {res_status}"

        self.controller.app.get_response(nvme_cmd)
        logger.info("Status Code: {}", nvme_cmd.rsp.response.sf.SC)

        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Flush")
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        logger.info("Deleted temp directory")
        logger.info("-"*100)
