# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send Connect command with Host ID cleared to 0h.
Expected: Connect Command error
'''
import pytest
import re
from src.macros import *
from utils.logging_module import logger
from test_cases.conftest import dummy
from lib.devlib.device_lib import ConnectDetails, Controller


@pytest.mark.skipif(True, reason="nvme-cli corrects the host-id before sending")
class TestNVMeConnectHostID:
    """Test case class for testing the Connect Command with Host ID cleared to 0h."""

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup test case by getting discovering the NQN '''

        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Connect Command with Host ID cleared to 0h")
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
        # End Discover Command

        logger.info("Setup Complete")
        logger.info("-"*35, "\n")

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
            self.connected_path = response
            logger.log("FAIL", "Connect passed for Host ID cleared to 0h")
            assert False, "Connect passed for Host ID cleared to 0h"

    def teardown_method(self):
        ''' Teardown test case by disconnecting the device '''

        print("\n\n", '-'*35)
        logger.info("Teardown TestCase: Connect Command with Host ID cleared to 0h")
        if self.connected_path:
            status, res = self.controller.app.submit_disconnect_cmd(
                device_path=self.connected_path)
            if status != 0:
                raise Exception(f"Disconnect failed: {res}")
        logger.info("Teardown Complete")
        logger.info("-"*100)
