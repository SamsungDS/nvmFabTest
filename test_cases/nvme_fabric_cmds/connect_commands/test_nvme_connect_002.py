'''
Send a connect command to Discovery Controller supporting change notification with Zero Keep Alive Time Out (KATO) value. 
Expected Output: Command response is successful
'''

import ctypes
import pytest, time

from src.macros import *
from src.utils.nvme_utils import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import ConnectDetails, Controller


class TestNVMeConnectKato:
    '''
    Send a connect command to Discovery Controller supporting change notification with Zero Keep Alive Time Out (KATO) value. 
    Expected Output: Command response is successful
    '''
    isChangeNotificationSupported = None

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        ''' Setup by checking if Change Notification is supported by discovery service '''

        print("\n", "-"*100)
        print("Setup TestCase: Connect Command with KATO")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        nqn = NVME_DISCOVERY_NQN

        # Start Connect Command to discovery controller
        status, response = self.controller.app.submit_connect_cmd(
            transport=tr, address=addr, svcid=svc, nqn=nqn)
        if status != 0 and status != 1:
            print(
                "-- -- Session Setup Error: Connect failed. Check the configuration details")
            raise Exception(
                "TestCase Setup Exeption: Unable to connect discovery controller")

        # Set device path to a new controller
        discovery_device =  response
        discovery_controller = Controller(discovery_device, application)

        # Sending identify controller to check OAES
        nvme_cmd = discovery_controller.cmdlib.get_identify_cmd()
        # Making it identify-self.controller command
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0x01

        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)
        ret_status = discovery_controller.app.submit_passthru(
            nvme_cmd, verify_rsp=True, async_run=False)
        discovery_controller.app.get_response(nvme_cmd)
        if ret_status != 0 and ret_status:
            raise Exception(f"Error sending identify controller: {ret_status}")
        if bin(result.OAES)[2] == '1':
            TestNVMeConnectKato.isChangeNotificationSupported = True
        else:
            TestNVMeConnectKato.isChangeNotificationSupported = False

        print("Change Notification is {}supported".format(
            "" if TestNVMeConnectKato.isChangeNotificationSupported else "not "))
        print("Setup Done: Connect Command with KATO")
        print("-"*35, "\n")

    def test_connect_discovery_zero_kato(self, connectDetails: ConnectDetails):
        '''
        Send Connect command with zero KATO value to Discovery Controller 
        if discovery change notification is supported.
        '''
        if not TestNVMeConnectKato.isChangeNotificationSupported:
            pytest.skip("Change Notification not supported")

        nqn = NVME_DISCOVERY_NQN
        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        nvme_cmd = self.controller.cmdlib.get_nvme_cmd()

        status, res = self.controller.app.submit_connect_cmd(
            tr, addr, svc, nqn, KATO_ZERO, duplicate=True)
        self.controller.app.get_response(nvme_cmd)
        status_code = nvme_cmd.rsp.response.sf.SC
        if status == 0 and status_code == 0:
            assert True
        else:
            assert False, "Connect failed for ZERO KATO"

    def teardown_method(self):
        ''' Teardown test case by disconnecting discovery controller '''

        print("\n\n", '-'*35)
        print("Teardown TestCase: Connect Command with KATO")

        status, res = self.controller.app.submit_disconnect_cmd(
            nqn=NVME_DISCOVERY_NQN)
        if status != 0:
            raise Exception(
                f"Disconnect from discovery controller failed: {res}")
        print("-"*100)
