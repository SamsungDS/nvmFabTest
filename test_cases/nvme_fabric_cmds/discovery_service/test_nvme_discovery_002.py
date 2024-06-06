'''
Send a Discovery Service with invalid host NQN
Expected output: Discovery fails
'''

import pytest
from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeDiscovery:

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        '''
        Send a Discovery Service with invalid host NQN
        Expected output: Discovery fails
        '''
        print("\n", "-"*100)
        print("Setup TestCase: Discovery Service")

        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

    def test_discovery_service(self, connectDetails: ConnectDetails):
        ''' Performing test '''

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        hostnqn = INVALID_NQN
        status, res = self.controller.app.submit_discover_cmd(
            tr, addr, svc, hostnqn = hostnqn)
        
        if status == 0:
            assert False, f"Discovery passed with invalid hostnqn"

        if "Invalid argument" not in res.decode():
            assert False, f"Discovery failed with unexpected error"

        assert True


    def teardown_method(self):
        '''Teardown test case'''

        print("\n\nTeardown TestCase: Discovery Service")
        print("-"*100)
