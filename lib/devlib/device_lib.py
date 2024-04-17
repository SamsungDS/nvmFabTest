
import sys 
sys.path.insert(1, "/root/nihal223/nvmfabtest")

from lib.applib.nvme_cli_lib import NVMeCLILib
from lib.cmdlib.commands_lib import NVMeCommandLib


class Controller():

    def __init__(self, dev_name, app_name) -> None:
        self.cmdlib = NVMeCommandLib(dev_name, app_name)
        self.dev_name = dev_name
        self.app_name = app_name
        if app_name.lower() == "nvme-cli":
            self.app = NVMeCLILib(dev_name)
        else:
            print("Error : ", app_name, app_name.lower)

    def submit_passthru_cmd(self, nvme_cmd, verify_rsp=True, async_run=False):
        res = self.app.submit_passthru(nvme_cmd, verify_rsp=verify_rsp, async_run=async_run)
        if res!=0:
            print("Error Message")
            return 1
        return 0

    def connect_cmd(self, connect_cmd, verify_rsp=True, async_run=False):
        res = self.app.submit_passthru(connect_cmd, verify_rsp=verify_rsp, async_run=async_run)
        if not res:
            print("Error Message")
    pass

class DeviceConfig:
    def __init__(self, device, application) -> None:
        self.device = device
        self.application = application

class ConnectDetails:
    def __init__(self, tr='', addr='', svc ='', index = 0) -> None:
        
        self.transport = tr
        self.address = addr
        self.svcid = svc
        self.index = index