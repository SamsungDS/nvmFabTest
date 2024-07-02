'''
Sends Get Features Command to retrieve the number of submission and completion queues.
Verify command executed successfully
'''

from src.macros import *
from test_cases.conftest import dummy
from lib.devlib.device_lib import Controller
import ctypes
import pytest


class TestNVMeGetFeatures:
    '''
    Sends Get Features Command to retrieve the number of submission and completion queues.
    Verify command executed successfully
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''
        print("\n", "-"*100)
        print("Setup TestCase: Get Features")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)
        print("Completed Setup\n\n")

    def test_get_features_cmd(self, dummy):
        ''' Sending the command and verifying response '''

        features_id = 7
        nvme_cmd = self.controller.cmdlib.get_get_features_cmd(features_id)

        res_status = self.controller.app.submit_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        if res_status != 0:
            self.controller.app.get_response(nvme_cmd)
            print("Status Code: ", nvme_cmd.rsp.response.sf.SC)
            assert False, f"Get Features failed: {res_status}"

        result = self.controller.app.get_passthru_result()

        result = int(result, 16)
        n_cq = result >> 16
        n_sq = result & 0xFFFF
        print("-- Number of Submission Queues:", n_sq)
        print("-- Number of Completion Queues:", n_cq)

        assert True

    def teardown_method(self):
        ''' Teardown of Test Case '''
        print("\n\nTeardown TestCase: Get Features")
        print("Completed Teardown")
        print("-"*100)
