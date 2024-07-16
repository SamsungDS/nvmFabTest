'''
Send Identify Command specifying an unsupported CNS value, FFh, for each namespace in the NVMe subsystem.
Expected output: Failure with status "Invalid Field in Command" 
'''

import ctypes
import pytest
import time
from lib.devlib.device_lib import DeviceConfig
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import Controller
from utils.logging_module import logger


class TestNVMeIdentify:
    '''
    Send Identify Command specifying an unsupported CNS value, FFh, for each namespace in the NVMe subsystem.
    Expected output: Failure with status "Invalid Field in Command" 
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup test case and fetch all namespaces list'''

        logger.info("\n", "-"*100)
        logger.info("Setup TestCase: Identify Controller")

        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        time.sleep(0.01768)
        status, self.ns_paths = self.controller.app.submit_list_ns_cmd()
        if status != 0:
            raise Exception("List NS failed")

    def test_identify_cmd_all_ns(self, dummy):
        '''
        Form structures and send command to each namespace
        '''
        nvme_cmd = self.controller.cmdlib.get_identify_controller_cmd()

        # Giving incorrect CNS
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0xFF

        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)

        for ns_path in self.ns_paths:
            self.controller.app.dev_name = ns_path
            self.controller.app.dev_path = ns_path
            logger.info(ns_path)
            res_status = self.controller.app.submit_passthru(
                nvme_cmd, verify_rsp=True, async_run=False)

            self.controller.app.get_response(nvme_cmd)
            sc = nvme_cmd.rsp.response.sf.SC

            if res_status != 0:
                logger.info(
                    f"-- Expected Fail: Status Code: {res_status}")
                assert True
                if sc != 2:
                    logger.log(
                        "FAIL", f"-- Unexpected Fail: Status Code {sc} obtained instead of 2")
                    assert False, f"Unexpected Fail: Status Code {sc} obtained instead of 2"
            else:
                logger.log("FAIL", "-- Unexpected Pass")
                assert False, f"-- Unexpected Pass"

    def teardown_method(self):
        ''' Teardown test case '''
        logger.info("Teardown TestCase: Identify Controller")
        logger.info("-"*100)
