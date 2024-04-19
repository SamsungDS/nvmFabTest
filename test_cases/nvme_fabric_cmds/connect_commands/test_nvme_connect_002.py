import sys
import ctypes
import pytest

sys.path.insert(1, "/root/nihal223/nvmfabtest/")
from lib.devlib.device_lib import ConnectDetails, Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from test_cases.conftest import dummy
from src.utils.nvme_utils import *
from src.macros import *

class TestNVMeConnectKato:
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, connectDetails: ConnectDetails):
        '''
        Setup for Connect Command with KATO value  
        '''
        print("-"*100)
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
        status, response = self.controller.app.submit_connect_cmd(transport=tr, address=addr, svcid=svc, nqn=nqn)
        if status!=0 and status!=1:
            print("-- -- Session Setup Error: Connect failed. Check the configuration details")
            raise Exception("TestCase Setup Exeption: Unable to connect discovery controller")
        
        #Get device path of connected discovery controller
        status, response = self.controller.app.submit_list_subsys_cmd()
        if status!=0:
            print("-- -- Command failed. Check if nvme cli tool is installed")
            raise Exception("TestCase Setup Exeption")
        
        
        status, response = get_dev_from_subsys(response, nqn)
        if status!=0:
            print(f"-- -- Test Case Setup Error: {response}")
            raise Exception("TestCase Setup Exeption")
        dev_path = response

        #Set device path to a new controller
       
        discovery_device = response
        discovery_controller = Controller(discovery_device, application)

        #Sending identify controller to check OAES
        nvme_cmd = discovery_controller.cmdlib.get_identify_cmd()
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0x01 # Making it identify-self.controller command
        
        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)

        ret_status = discovery_controller.submit_passthru_cmd(nvme_cmd, verify_rsp=True, async_run=False)
        discovery_controller.app.get_response(nvme_cmd)
        if ret_status!=0:
            raise Exception("Error sending identify controller")
        if bin(result.OAES)[2]=='1':
            self.isChangeNotificationSupported = True
        else:
            self.isChangeNotificationSupported = False
        print("Change Notification is %ssupported".format("" if self.isChangeNotificationSupported else "not "))
        print("Setup Done: Connect Command with KATO")
        print("-"*35, "\n")
        

    def test_connect_discovery_kato(self, connectDetails: ConnectDetails):
        '''
        Send Connect command with zero KATO value to Discovery Controller 
        if discovery change notification is supported.
        
        Expected: Command response is successful
        '''
        nqn = NVME_DISCOVERY_NQN
        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        nvme_cmd = self.controller.cmdlib.get_nvme_cmd()

        if self.isChangeNotificationSupported:
            status, res = self.controller.app.submit_connect_cmd(tr, addr, svc, nqn, KATO_ZERO)
            self.controller.app.get_response(nvme_cmd)
            status_code = nvme_cmd.rsp.response.sf.SC
            if status==0 and status_code==0:
                assert True
            else:
                assert False, "Connect failed for ZERO KATO"


    def teardown_method(self):
        print("\n\n", '-'*35)
        print("Teardown TestCase: Connect Command with KATO")
        status, res = self.controller.app.submit_disconnect_cmd(nqn=NVME_DISCOVERY_NQN)
        if status!=0:
            raise Exception(f"Disconnect from discovery controller failed: {res}")
        print("-"*100)