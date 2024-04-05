import sys
import ctypes
import pytest
import json

sys.path.insert(1, "/root/nihal223/nvmfabtest/")
from lib.devlib.device_lib import Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from test_cases.conftest import dummy

class TestNVMeIdentify:
    def setup_method(self):
        print("Setup: Identify Controller")
        

    def teardown_method(self):
        print("Teardown: Identify Controller")

    def test_identify_cmds(self, dummy):
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        controller = Controller(device, application) # /dev/nvme1 ; nvme-cli|libnve

        nvme_cmd = controller.cmdlib.get_identify_cmd()
        
        nvme_cmd.cmd.identify_cmd.NSID = 0
        nvme_cmd.rsp.identify_rsp.SC = 10
        result = IdentifyControllerData()
        nvme_cmd.buff = ctypes.addressof(result)
        res_status = controller.submit_passthru_cmd(nvme_cmd, verify_rsp=True, async_run=False)
        if res_status!=0:
            assert False
        
        if ("S79LNG0W600229" == result.SN.decode().strip()):
            assert True
        else:
            assert False
        


# a = TestNVMeIdentify()
# a.setup_method()
# a.test_identify_cmds() 