'''
Verify connect command with NVM Subsystem NQN value - "not matching" the values that the NVM subsystem is configured to support.
Expected output: Failure with status "Connect Invalid Parameters"
'''
import pytest
import re

from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeConnectNQN:
    '''
    Verify connect command with NVM Subsystem NQN value - "not matching" the values that the NVM subsystem is configured to support.
    Expected output: Failure with status "Connect Invalid Parameters"
    '''
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup test case by getting discovering the NQN '''

        print("\n", "-"*100)
        print("Setup TestCase: Connect Command with invalid subsystem NQN")
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

        print("Setup Done: Connect Command with invalid subsystem NQN")
        print("-"*35, "\n")

    def test_connect_invalid_subnqn(self, connectDetails: ConnectDetails):
        ''' Send Connect command with invalid subsystem NQN '''
        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        nqn = self.nqn

        nqn = nqn+"ZzZ%$d"
        # Start Connect Command
        status, response = self.controller.app.submit_connect_cmd(
            transport=tr, address=addr, svcid=svc, nqn=nqn, duplicate=True)

        if status != 0:
            print("-- Expected Failure in Connect Command")
            assert True
        else:
            assert False, "Connect passed for incorrect subsytem nqn"

    def teardown_method(self):
        ''' Teardown test case by disconnecting the device '''

        print("\n\n", '-'*35)
        print("Teardown TestCase: Connect Command with invalid subsystem NQN")
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