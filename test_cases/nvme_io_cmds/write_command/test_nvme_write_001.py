# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send an NVM Write command to write one block size of data.
Verify success.
'''

import ctypes
import shutil
import pytest
from src.macros import *
from test_cases.conftest import fabConfig
from utils.logging_module import logger
from lib.devlib.device_lib import Controller


class TestNVMeWrite:
    '''
    Send an NVM Write command to write one block size of data.
    Verify command success.
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, fabConfig):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n"+"-"*100)
        logger.info("Setup TestCase: Write")
        self.fabConfig = fabConfig
        device = self.fabConfig.device
        application = self.fabConfig.application
        self.controller = Controller(device, application)

        self.lba_size = self.controller.app.get_device_lba_size()

    def test_write_cmd(self, fabConfig):
        ''' Sending the command and verifying response '''
        data_len = 512
        data = None
        nvme_cmd = self.controller.cmdlib.get_write_cmd()

        with open("assets/random_bytes.txt", 'rb') as f:
            data = ctypes.c_buffer(f.read(data_len), data_len)
            
        nvme_cmd.buff = ctypes.addressof(data)
        nvme_cmd.buff_size = data_len
        
        upper = 0
        start_lba = 0x123
        if start_lba > 0xFFFFFFFF:
            upper = start_lba >> 32
        lower = start_lba & 0x00000000FFFFFFFF

        n_blocks =  data_len // self.lba_size

        nvme_cmd.cmd.generic_command.cdw10.raw = lower
        nvme_cmd.cmd.generic_command.cdw11.raw = upper & 0xFFFFFFFF
        
        nvme_cmd.cmd.generic_command.cdw12.raw = n_blocks - 1
        
        res_status = self.controller.app.submit_io_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        
        if res_status != 0:
            assert False, f"Write failed: {res_status}"

        self.controller.app.get_response(nvme_cmd)
        logger.info("Status Code: {}", nvme_cmd.rsp.response.sf.SC)

        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: Write")
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        logger.info("Deleted temp directory")
        logger.info("-"*100)
