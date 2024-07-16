'''
Send a connect command with host dhchap set.
Expected output: Connect command response is successful
'''

import pytest
import re
from src.macros import *
from utils.logging_module import logger
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import *


class TestNVMeAuthConnect:
    '''
    Send a connect command with host dhchap set.
    Expected output: Connect command response is successful
    '''
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, authDetails: AuthDetails):
        ''' Setup Test Case by initialization of objects '''

        self.skipped = False
        if authDetails.should_test.lower() != "true":
            self.skipped = True
            pytest.skip("Authentication Tests Disabled")

        logger.info("\n", "-"*100)
        logger.info("Setup TestCase: Auth Connect Command")

        self.connectIsSuccess = None
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        tr = authDetails.transport
        addr = authDetails.address
        svc = authDetails.svcid
        index = authDetails.index
        hostnqn = authDetails.hostnqn

        # Start Discover Command
        if hostnqn and len(hostnqn) != 0:
            status, response = self.controller.app.submit_discover_cmd(
                transport=tr, address=addr, svcid=svc, hostnqn=hostnqn)
        else:
            status, response = self.controller.app.submit_discover_cmd(
                transport=tr, address=addr, svcid=svc)

        if status != 0:
            logger.error(
                "-- -- TestCase Setup Error: Discover command failed. Check the configuration details")
            raise Exception("TestCase Setup Exception")

        self.nqn = self.controller.app.get_nqn_from_discover(response, index)
        # End Discover Command

        # List-subsys
        status, response = self.controller.app.submit_list_subsys_cmd()
        if status != 0:
            logger.error("-- -- TestCase Setup Error: Check if nvme cli tool is installed")
            return status, response
        self.all_nvme_setup: list = re.findall(r"nvme\d", response.decode())
        self.all_nvme_setup.sort()

        logger.info("Setup Done: Auth Connect Command")
        logger.info("-"*35, "\n")

    def test_auth_connect_host_dhchap(self, authDetails: AuthDetails):
        ''' Performing test by sending connect command to discovery NQN '''

        tr = authDetails.transport
        addr = authDetails.address
        svc = authDetails.svcid
        dhchap_host = authDetails.dhchap_host if authDetails.dhchap_host and len(
            authDetails.dhchap_host) != 0 else None
        dhchap_ctrl = authDetails.dhchap_host if authDetails.dhchap_ctrl and len(
            authDetails.dhchap_ctrl) != 0 else None
        hostnqn = authDetails.hostnqn if authDetails.hostnqn and len(
            authDetails.hostnqn) != 0 else None

        status, res = self.controller.app.submit_connect_cmd(
            tr, addr, svc, self.nqn, dhchap_host=dhchap_host,
            dhchap_ctrl=dhchap_ctrl, hostnqn=hostnqn)

        if status != 0:
            assert False, f"Sending Auth Connect Command failed: {status}"
        else:
            self.connectIsSuccess = True
            nvme_cmd = self.controller.cmdlib.get_nvme_cmd()
            self.controller.app.get_response(nvme_cmd)
            status_code = nvme_cmd.rsp.response.sf.SC
            if status_code != 0:
                assert False, f"Auth Connect Command failed with Status Code {
                    status_code}"
            else:
                assert True
    
    def teardown_method(self):
        '''Teardown test case by disconnecting '''
        if self.skipped:
            return
        logger.info("\n\nTeardown TestCase: Auth Connect Command")

        status, response = self.controller.app.submit_list_subsys_cmd()
        if status != 0:
            logger.error("-- -- TestCase Teardown Error")
            return status, response

        self.all_nvme_teardown: list = re.findall(r"nvme\d", response.decode())
        self.all_nvme_teardown.sort()
        if len(self.all_nvme_teardown)-len(self.all_nvme_setup) == 1:
            path = "/dev/" + self.all_nvme_teardown[-1]

            status, res = self.controller.app.submit_disconnect_cmd(
                device_path=path)
            if status != 0:
                raise Exception(f"Disconnect failed: {res}")

        logger.info("Teardown Complete: Auth Connect Command")
        logger.info("-"*100)
