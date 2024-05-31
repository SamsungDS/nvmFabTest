'''
Verify connect command with valid fields(SUBNQN, TRADDR, TRSVCID, TRTYPE).
Expected output: Connect command response is successful
'''
import pytest
import re

from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeConnect:
    '''
    Verify connect command with valid fields(SUBNQN, TRADDR, TRSVCID, TRTYPE).
    Expected output: Connect command response is successful
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup test case by getting discovering the NQN '''

        print("\n", "-"*100)
        print("Setup TestCase: Connect Command with valid fields")

        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)
        self.connected_path = None

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

        print("Setup Done: Connect Command with Valid Fields")
        print("-"*35, "\n")

    def test_connect_valid_fields(self, connectDetails: ConnectDetails):
        ''' Send Connect command with valid fields '''

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        nqn = self.nqn
        nvme_cmd = self.controller.cmdlib.get_nvme_cmd()

        # Start Connect Command
        status, response = self.controller.app.submit_connect_cmd(
            transport=tr, address=addr, svcid=svc, nqn=nqn, duplicate=True)
        self.controller.app.get_response(nvme_cmd)
        status_code = nvme_cmd.rsp.response.sf.SC
        if status == 0 and status_code == 0:
            self.connected_path = response
            assert True
        else:
            assert False, "Connect failed for valid fields"

    def teardown_method(self):
        ''' Teardown test case by disconnecting the device '''

        print("\n\n", '-'*35)
        print("Teardown TestCase: Connect Command with valid fields")
        
        if self.connected_path:
            status, res = self.controller.app.submit_disconnect_cmd(
                    device_path=self.connected_path)
            if status != 0:
                raise Exception(f"Disconnect failed: {res}")
        print("Teardown Complete")
        print("-"*100)
