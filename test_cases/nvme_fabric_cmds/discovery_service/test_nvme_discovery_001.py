'''
Send a Get Log Page command to Discovery Controller and retrieve subsystem NQN

Expected output: Valid NQN retrieved
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
        Send a Get Log Page command to Discovery Controller and retrieve subsystem NQN
        Expected output: Valid NQN retrieved
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
        status, res = self.controller.app.submit_discover_cmd(
            tr, addr, svc)

        if status != 0:
            assert False, f"Discovery failed with Status Code {status}"
        try:
            nqn = self.controller.app.get_nqn_from_discover(res, 0)
        except Exception as e:
            assert False, f"Discovery log not in proper format: {e.__str__}"

        if len(nqn) == 0:
            assert False, "Discovery log not in proper format2"

        if nqn[:3] != "nqn":
            assert False, "Discovery log not in proper format3"

        assert True

    def teardown_method(self):
        '''Teardown test case'''

        print("\n\nTeardown TestCase: Discovery Service")
        print("-"*100)
