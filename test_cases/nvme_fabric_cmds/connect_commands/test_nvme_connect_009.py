'''
Send Connect and Disconnect command with different number of IO queues.
Expected: Connect Command successful
'''

import pytest
import re

from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeConnectIOQueues:
    '''
    Send Connect and Disconnect command with different number of IO queues.
    Expected: Connect Command successful
    '''
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup test case by getting discovering the NQN '''

        print("\n", "-"*100)
        print("Setup TestCase: Connect Command with different number of IO queues")
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

    def test_connect_nr_io_queues(self, connectDetails: ConnectDetails):
        ''' Send Connect and Disconnect command with different number of IO queues '''

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        nqn = self.nqn

        nr_io_queues_list = [4, 8, 16, 32]

        for nr_io_queues in nr_io_queues_list:
            # Start Connect Command
            status, response = self.controller.app.submit_connect_cmd(
                transport=tr, address=addr, svcid=svc, nqn=nqn, duplicate=True, nr_io_queues=nr_io_queues)

            if status == 0:
                assert True
            else:
                assert False, "Connect failed for different number of io queues"

            # Getting connection path
            status, response = self.controller.app.submit_list_subsys_cmd()
            if status != 0:
                print("-- -- TestCase Setup Error: Check if nvme cli tool is installed")
                return status, response
            all_nvme_devices: list = re.findall(r"nvme\d", response.decode())
            all_nvme_devices.sort()

            if len(all_nvme_devices)-len(self.all_nvme_setup) == 1:
                path = "/dev/" + all_nvme_devices[-1]
            # Start Disconnect Command
            status, res = self.controller.app.submit_disconnect_cmd(
                device_path=path)
            if status != 0:
                assert False, "Disconnect failed for different number of io queues"
            else:
                assert True

    def teardown_method(self):
        ''' Teardown test case by disconnecting the device '''

        print("\n\n", '-'*35)
        print("Teardown TestCase: Connect Command with different number of IO queues")
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
