'''
Send Identify Command specifying an unsupported CNS value, FFh, for each namespace in the NVMe subsystem.
Expected output: Failure with status "Invalid Field in Command" 
'''
import sys
import ctypes
import pytest

sys.path.insert(1, "/root/nihal223/nvmfabtest/")
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from test_cases.conftest import dummy

class TestNVMeIdentify:
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        ''' Setup test case and fetch all namespaces list'''
        
        print("\n", "-"*100)
        print("Setup TestCase: Identify Controller")

        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        status, self.ns_paths = self.controller.app.submit_list_ns_cmd()
        if status!=0:
            raise Exception("List NS failed")

    def test_identify_cmd_all_ns(self, dummy):
        '''
        Form structures and send command to each namespace
        '''
        nvme_cmd = self.controller.cmdlib.get_identify_cmd()
        
        # Giving incorrect CNS
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0xFF
        
        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)

        for ns_path in self.ns_paths:
            self.controller.app.dev_path = ns_path

            res_status = self.controller.submit_passthru_cmd(nvme_cmd, verify_rsp=True, async_run=False)
            
            self.controller.app.get_response(nvme_cmd)
            sc = nvme_cmd.rsp.response.sf.SC
            if sc == 2 or res_status!=0:
                print(f"-- Expected Fail: Invalid Field in Command. Status Code: {sc}")
                assert True
            elif sc!=0:
                assert False, f"-- Error response received with unexpected Status Code: {sc}"
            else:
                assert False, f"-- Unexpected Pass: Status Code {sc} obtained instead of 2"
    
    def teardown_method(self):
        ''' Teardown test case'''
        print("Teardown TestCase: Identify Controller")
        print("-"*100)
        
from lib.devlib.device_lib import DeviceConfig
if __name__=='__main__':
    dum = DeviceConfig("/dev/nvme2", "nvme-cli")
    TestNVMeIdentify().test_identify_cmd_all_ns(dum)
