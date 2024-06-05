'''
Send a connect command with ctrl dhchap set.
Expected output: Connect command response is successful
'''

import pytest
import re
from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeAuthConnect:
    '''
    Send a connect command with ctrl dhchap set.
    Expected output: Connect command response is successful
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup Test Case by initialization of objects '''

        print("\n", "-"*100)
        print("Setup TestCase: Auth Connect Command")

        self.connectIsSuccess = None
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        index = connectDetails.index

        # Start Discover Command
        status, response = self.controller.app.submit_discover_cmd(
            transport=tr, address=addr, svcid=svc)
        if status != 0:
            print(
                "-- -- TestCase Setup Error: Discover command failed. Check the configuration details")
            raise Exception("TestCase Setup Exception")

        self.nqn = self.controller.app.get_nqn_from_discover(response, index)
        # End Discover Command

        # List-subsys
        status, response = self.controller.app.submit_list_subsys_cmd()
        if status != 0:
            print("-- -- TestCase Setup Error: Check if nvme cli tool is installed")
            return status, response
        self.all_nvme_setup: list = re.findall(r"nvme\d", response.decode())
        self.all_nvme_setup.sort()

        print("Setup Done: Auth Connect Command")
        print("-"*35, "\n")

    def test_auth_connect_ctrl_dhchap(self, connectDetails: ConnectDetails):
        ''' Performing test by sending connect command to discovery NQN '''

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        index = connectDetails.index

        dhchap_ctrl = "dummydummydummydummydummydummydu"

        status, res = self.controller.app.submit_connect_cmd(
            tr, addr, svc, self.nqn, dhchap_ctrl=dhchap_ctrl, duplicate=True)
        
        if status != 0:
            assert False, f"Sending Auth Connect Command failed: {status}"
        else:
            self.connectIsSuccess = True
            nvme_cmd = self.controller.cmdlib.get_nvme_cmd()
            self.controller.app.get_response(nvme_cmd)
            status_code = nvme_cmd.rsp.response.sf.SC
            if status_code != 0:
                assert False, f"Auth Connect Command failed with Status Code {status_code}"
            else:
                assert True

    def teardown_method(self):
        '''Teardown test case by disconnecting '''
        print("\n\nTeardown TestCase: Auth Connect Command")

        status, response = self.controller.app.submit_list_subsys_cmd()
        if status != 0:
            print("-- -- TestCase Setup Error: Check if nvme cli tool is installed")
            return status, response

        self.all_nvme_teardown: list = re.findall(r"nvme\d", response.decode())
        self.all_nvme_teardown.sort()
        if len(self.all_nvme_teardown)-len(self.all_nvme_setup) == 1:
            path = "/dev/" + self.all_nvme_teardown[-1]

            status, res = self.controller.app.submit_disconnect_cmd(
                device_path=path)
            if status != 0:
                raise Exception(f"Disconnect failed: {res}")
        
        print("Teardown Complete: Auth Connect Command")
        print("-"*100)
