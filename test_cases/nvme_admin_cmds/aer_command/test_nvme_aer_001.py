# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send more Asynchronous Event Request commands than the limit specified in AERL

Verify command fails with Asynchronous Event Request Limit Exceeded (05h).
'''

import ctypes
import time
import pytest
from src.macros import *
from test_cases.conftest import dummy
from utils.logging_module import logger
from lib.devlib.device_lib import Controller


class TestNVMeAER:
    '''
    Send more Asynchronous Event Request commands than the limit specified in AERL

    Verify command fails with Asynchronous Event Request Limit Exceeded (05h).
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        logger.info("\n"+"-"*100)
        logger.info("Setup TestCase: AER")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        # Send Identify Controller to get AER Limit
        self.p = []
        nvme_cmd = self.controller.cmdlib.get_identify_controller_cmd()
        result = ctypes.create_string_buffer(4096)
        nvme_cmd.buff = ctypes.addressof(result)

        res_status = self.controller.app.submit_admin_passthru(
                nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            logger.log("FAIL", "Identify failed during setup")
            assert False, f"Identify failed: {res_status}"

        self.aer_limit = int(result.raw[259]) 

    def test_aer_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        nvme_cmd = self.controller.cmdlib.get_aer_cmd()

        for _ in range(self.aer_limit):
            process = self.controller.app.submit_admin_passthru(
                nvme_cmd, verify_rsp=True, async_run=True)
            self.p.append(process)
            
            time.sleep(0.1)
            if process.poll() != None:
                
                logger.log("FAIL", f"AER failed before limit: {process.poll()}")
                assert False, f"AER failed before limit: {process.poll()}"

        # AER Limit is now reached
        process = self.controller.app.submit_admin_passthru(
            nvme_cmd, verify_rsp=True, async_run=True)
        
        tim = time.time()
        while process.poll() is None:
            if time.time()-tim == 2:
                break

        if process.poll() is None:
            logger.log("FAIL", "AER passed after limit")
            process.kill()
            assert False, f"AER passed after limit"

        self.controller.app.stdout, self.controller.app.stderr = process.communicate()
        self.controller.app.ret_code = process.returncode

        stderr = self.controller.app.stderr
        if len(stderr) != 0 and self.controller.app.ret_code != 0:
            logger.warning(f"-- -- Command execution failed: {stderr[:stderr.find(b'\n')]}")
        logger.success("-- -- Command execution success")

        self.controller.app.get_response(nvme_cmd)
        status_code = nvme_cmd.rsp.response.sf.SC
        
        if status_code!=0x05:
            logger.log("FAIL", f"AER failed with incorrect status code: {status_code}")
            assert False, f"AER failed with incorrect status code: {status_code}"
        
        logger.success("AER Command failed with correct Status Code")
        logger.info("Status Code: {}", status_code)
        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        logger.info("Teardown TestCase: AER")
        for p in self.p:
            p.kill()
            logger.info("Process killed")
        logger.info("-"*100)
