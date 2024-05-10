'''
Send Connect command with Host ID cleared to 0h.
Expected: Connect Command error
'''
import sys
import pytest
import re

sys.path.insert(1, "/root/nihal223/nvmfabtest/")
from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeConnectHostID:
    """Test case class for testing the Connect Command with Host ID cleared to 0h."""

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup test case by getting discovering the NQN '''

        print("\n", "-"*100)
        print("Setup TestCase: Connect Command with Host ID cleared to 0h")
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

        print("Setup Complete")
        print("-"*35, "\n")

    def test_connect_zero_hostid(self, connectDetails: ConnectDetails):
        ''' Send Connect command with Host ID cleared to 0h '''

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        nqn = self.nqn

        hostid = 0

        # Start Connect Command
        status, response = self.controller.app.submit_connect_cmd(
            transport=tr, address=addr, svcid=svc, nqn=nqn, duplicate=True, hostid=hostid)

        if status != 0:
            print("-- Expected Failure in Connect Command")
            assert True
        else:
            assert False, "Connect passed for Host ID cleared to 0h"

    def teardown_method(self):
        ''' Teardown test case by disconnecting the device '''

        print("\n\n", '-'*35)
        print("Teardown TestCase: Connect Command with Host ID cleared to 0h")
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
        print("Teardown Complete")
        print("-"*100)
