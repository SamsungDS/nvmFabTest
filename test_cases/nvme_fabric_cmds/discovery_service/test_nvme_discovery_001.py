# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Send a Get Log Page command to Discovery Controller and retrieve subsystem NQN

Expected output: Valid NQN retrieved
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
        Send a Get Log Page command to Discovery Controller and retrieve subsystem NQN
        Expected output: Valid NQN retrieved
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
        status, res = self.controller.app.submit_discover_cmd(
            tr, addr, svc)

        if status != 0:
            assert False, f"Discovery failed with Status Code {status}"
        try:
            nqn = self.controller.app.get_nqn_from_discover(res, 0)
        except Exception as e:
            logger.exception(e)
            assert False, f"Discovery log not in proper format: {e.__str__}"

        if len(nqn) == 0:
            logger.log("FAIL", "Discovery log not in proper format")
            assert False, "Discovery log not in proper format"

        if nqn[:3] != "nqn":
            logger.log("FAIL", "Discovery log not in proper format")
            assert False, "Discovery log not in proper format"

        assert True

    def teardown_method(self):
        '''Teardown test case'''

        logger.info("\n\nTeardown TestCase: Discovery Service")
        logger.info("-"*100)
