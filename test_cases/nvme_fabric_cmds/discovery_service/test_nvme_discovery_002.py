# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-2-Clause

'''
Send a Discovery Service with invalid host NQN
Expected output: Discovery fails
'''

import pytest
from src.macros import *
from utils.logging_module import logger
from test_cases.conftest import fabConfig
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeDiscovery:

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, fabConfig):
        '''
        Send a Discovery Service with invalid host NQN
        Expected output: Discovery fails
        '''
        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Discovery Service")

        self.fabConfig = fabConfig
        device = self.fabConfig.device
        application = self.fabConfig.application
        self.controller = Controller(device, application)

    def test_discovery_service(self, connectDetails: ConnectDetails):
        ''' Performing test '''

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        hostnqn = INVALID_NQN
        status, res = self.controller.app.submit_discover_cmd(
            tr, addr, svc, hostnqn=hostnqn)

        if status == 0:
            logger.log("FAIL", "Discovery passed with invalid hostnqn")
            assert False, f"Discovery passed with invalid hostnqn"

        if "Invalid argument" not in res.decode():
            logger.log("FAIL", "Discovery failed with unexpected error")
            assert False, f"Discovery failed with unexpected error"

        assert True

    def teardown_method(self):
        '''Teardown test case'''

        logger.info("\n\nTeardown TestCase: Discovery Service")
        logger.info("-"*100)
