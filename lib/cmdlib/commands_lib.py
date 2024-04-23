import sys
sys.path.insert(1, "/root/nihal223/nvmfabtest")

from lib.applib.nvme_cli_lib import NVMeCLILib
from lib.structlib.nvme_struct_main_lib import NVMeCommand
from lib.structlib.struct_admin_data_lib import IdentifyControllerData 



class NVMeCommandLib:
    def __init__(self, app_name, dev_name='', connectDetails=None) -> None:
        self.dev_name = dev_name
        self.app_name = app_name
        if app_name.lower == "nvme-cli":
            self.app = NVMeCLILib(dev_name)
        elif app_name.lower == "libnvme":
            pass #self.app = Libnvme(dev_name)
        else:
            pass

    def get_nvme_cmd(self):                
        nvme_cmd = NVMeCommand()
        return nvme_cmd
    
    def get_identify_cmd(self):
        nvme_cmd = self.get_nvme_cmd()
        nvme_cmd.buff_size = 4096
        nvme_cmd.cmd.identify_cmd.cdw0.OPC = 0x06
        
        nvme_cmd.cmd.identify_cmd.NSID = 0
        # nvme_cmd.rsp.response.SC = 10

        return nvme_cmd
    



    
    

    """
    
    def submit_passthru_cmd(self, nvme_cmd, verify_rsp=True, async_run=False):
        return self.app.submit_passthru(nvme_cmd, verify_rsp=verify_rsp, async_run=async_run)

    def connect_cmd(self, cmdrsp_obj):
        command = cmdrsp_obj.nvme_cmd.nvme_identify_cmd
        response = cmdrsp_obj.nvme_rsp.nvme_identify_rsp
        data = cmdrsp_obj.dev_obj.nvme_data
        data_size = cmdrsp_obj.dev_obj.nvme_data_size

        res = self.app.submit_passthru(command, response, data, data_size)
        if not res:
            print("Error Message")
    """

if __name__ == '__main__':
    NVMeCommandLib('adsd0').parse_discover_cmd(b'asdasda_subnqn: NQN.dfasdcb \n fvgbfcb_subnqn: NQN.sad   \n dfs')
    pass