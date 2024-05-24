'''
Send a connect command with ctrl dhchap set.
Expected output: Connect command response is successful
'''

import pytest
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
    def setup_method(self, dummy):
        ''' Setup Test Case by initialization of objects '''

        print("\n", "-"*100)
        print("Setup TestCase: Connect Command")

        self.connectIsSuccess = None
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_auth_connect_ctrl_dhchap(self, connectDetails: ConnectDetails):
        ''' Performing test by sending connect command to discovery NQN '''

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
        if self.connectIsSuccess:
            status, res = self.controller.app.submit_disconnect_cmd(
                nqn=self.nqn)
            if status != 0:
                raise Exception(
                    f"Disconnect from discovery controller failed: {res}")
        print("-"*100)
