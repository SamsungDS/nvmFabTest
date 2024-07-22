# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send Connect and Disconnect command with different number of IO queues.
Expected: Connect Command successful
'''

import pytest
import re
from src.macros import *
from utils.logging_module import logger
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

        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Connect Command with different number of IO queues")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)
        self.connected_paths = []

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        index = connectDetails.index

        # Start Discover Command
        status, response = self.controller.app.submit_discover_cmd(
            transport=tr, address=addr, svcid=svc)
        if status != 0:
            logger.error(
                "-- -- TestCase Setup Error: Discover command failed. Check the configuration details")
            raise Exception("TestCase Setup Exception")

        self.nqn = self.controller.app.get_nqn_from_discover(response, index)
        # End Discover Command

        logger.info("Setup Complete")
        logger.info("-"*35 + "\n")

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
                self.connected_paths.append(response)
                assert True
            else:
                logger.log("FAIL", "Connect failed for different number of io queues")
                assert False, "Connect failed for different number of io queues"

    def teardown_method(self):
        ''' Teardown test case by disconnecting the device '''

        logger.info('-'*35)
        logger.info("Teardown TestCase: Connect Command with different number of IO queues")

        for path in self.connected_paths:
            if not path or path == '':
                continue
            status, res = self.controller.app.submit_disconnect_cmd(
                device_path=path)
            if status != 0:
                raise Exception(f"Disconnect failed: {res}")

        logger.info("Teardown Complete")
        logger.info("-"*100)
