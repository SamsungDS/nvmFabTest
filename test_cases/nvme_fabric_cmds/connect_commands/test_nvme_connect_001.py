import sys
import ctypes
import pytest
import json
import re


sys.path.insert(1, "/root/nihal223/nvmfabtest/")
from lib.devlib.device_lib import ConnectDetails, Controller
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from test_cases.conftest import dummy
from src.utils.nvme_utils import *

from src.macros import *

class TestNVMeConnect:
    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy):
        print("-"*100)
        print("Setup TestCase: Connect Command")
        self.dummy = dummy
        device = self.dummy.device
        application = self.dummy.application
        self.controller = Controller(device, application)

        
    def teardown_method(self):
        print("\n\nTeardown TestCase: Connect Command")
        status, res = self.controller.app.submit_disconnect_cmd(nqn=NVME_DISCOVERY_NQN)
        if status!=0:
            raise Exception(f"Disconnect from discovery controller failed: {res}")
        print("-"*100)

        

    def test_connect_discovery(self, connectDetails: ConnectDetails):
        nqn = NVME_DISCOVERY_NQN
        tr = connectDetails.transport
        addr = connectDetails.address
        svc = connectDetails.svcid
        status, res = self.controller.app.submit_connect_cmd(tr, addr, svc, nqn)
        if status!=0:
            assert False, "Sending Connect Command failed"
        else:
            nvme_cmd = self.controller.cmdlib.get_nvme_cmd()
            self.controller.app.get_response(nvme_cmd)
            status_code = nvme_cmd.rsp.response.sf.SC
            if status_code!=0:
                assert False, f"Connect Command failed with Status Code {status_code}"
            else:
                assert True

