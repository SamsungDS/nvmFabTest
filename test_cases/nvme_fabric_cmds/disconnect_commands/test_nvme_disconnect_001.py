'''
Send a disconnect command to a fabric device.
Expected output: Disconnect command response is successful
'''

import pytest
from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeDisconnect:
    '''
    Send a disconnect command to a fabric device.
    Expected output: Disconnect command response is successful
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup Test Case by initialization of objects '''

        print("\n", "-"*100)
        print("Setup TestCase: Connect Command")

        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        nqn = NVME_DISCOVERY_NQN
        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        status, res = self.controller.app.submit_connect_cmd(
            tr, addr, svc, nqn)
        if status != 0:
            raise ConnectionError(f"Sending Connect Command failed: {status}")
        else:
            nvme_cmd = self.controller.cmdlib.get_nvme_cmd()
            self.controller.app.get_response(nvme_cmd)
            status_code = nvme_cmd.rsp.response.sf.SC
            if status_code != 0:
                raise ConnectionError(
                    f"Connect Command failed with Status Code {status_code}")

    def test_disconnect(self, connectDetails: ConnectDetails):
        ''' Performing test by sending disconnect command '''
        status, res = self.controller.app.submit_disconnect_cmd(
            nqn=NVME_DISCOVERY_NQN)
        if status != 0:
            assert False, f"Disconnect from discovery controller failed: {res}"

        assert True

    def teardown_method(self):
        '''Teardown test case '''

        print("\n\nTeardown TestCase: Connect Command")

        print("-"*100)
