import sys

sys.path.insert(1, "/root/nihal223/nvmfabtest")

from lib.cmdlib.commands_lib import NVMeCommandLib
from lib.structlib.struct_base_lib import GenericCommand
import os, json, re
from lib.structlib.nvme_struct_main_lib import NVMeCommand, NVMeRspStruct
from utils.logging_module import logger
import ctypes
from lib.applib.nvme_cli_lib import ApplicationLib 
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.structlib.struct_fabric_libnvme_lib import *

class Libnvme():
    def __init__(self, dev_path) -> None:
        print("LIBNVME init")
        if re.match(r"\A/dev/nvme[0-9]+(n[0-9]+)?\Z", dev_path):
            self.dev_name = dev_path[5:]
        self.command = None
        self.response = None
        self.cmdlib = NVMeCommandLib("libnvme")
        libnvme_path = Libnvme.get_libnvme_path()
        self.libnvme = ctypes.CDLL(libnvme_path)

    @staticmethod
    def get_libnvme_path():
        f = open("config/ts_config.json")
        ts_config = json.load(f)
        f.close()
        
        #Finding system's libnvme.so file
        if ts_config["libnvme_path"].lower() == "auto":
            for root, dirs, files in os.walk("/usr/"):
                if "libnvme.so" in files:
                    return os.path.join(root, "libnvme.so")
                
            for root, dirs, files in os.walk("/"):
                if "libnvme.so" in files:
                    return os.path.join(root, "libnvme.so")
    
            print("Not able to find libnvme.so. Give the path manually in ts_config.json.")
            raise FileNotFoundError("Not able to find libnvme.so. Give the path manually in ts_config.json.")
    
        elif ts_config["libnvme_path"].endswith("libnvme.so") and os.path.isfile(ts_config["libnvme_path"]):
            return ts_config["libnvme_path"]
        else:
            print("libnvme.so path not correct. Set to \"auto\" to find automatically.")
            raise FileNotFoundError("libnvme.so path not correct. Set to \"auto\" to find automatically.")
    
    def nvme_open(self):
        device_name = self.dev_name
        nvme_open = self.libnvme.nvme_open
        nvme_open.argtypes = [ctypes.c_char_p]
        nvme_open.restype = ctypes.c_int
        device_descriptor = nvme_open(device_name.encode())
        if device_descriptor < 0:
            return device_descriptor, f"Failed to open NVMe device {device_name}. Error code {device_descriptor}"
        else:
            self.device_descriptor = device_descriptor
            return 0, ""
        
    def submit_list_ns_cmd(self):
        nvme_cmd = self.cmdlib.get_identify_cmd()
        result = ctypes.create_string_buffer(4096)

        nvme_cmd.buff = ctypes.addressof(result)
        command = nvme_cmd.cmd.generic_command
        nvme_cmd.cmd.generic_command.dptr.sgl.data_len = 4096
        nvme_cmd.cmd.generic_command.dptr.sgl.addr = nvme_cmd.buff
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0x02

        status, error = self.nvme_open()
        if status!=0:
            return status, error
        
        libnvme_submit_admin_passthru = self.libnvme.nvme_submit_admin_passthru
        libnvme_submit_admin_passthru.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
        libnvme_submit_admin_passthru.restype = ctypes.c_int32
        print("Structure passed to libnvme is at address ", hex(command.dptr.sgl.addr))
        
        status = libnvme_submit_admin_passthru(self.device_descriptor, ctypes.addressof(command), None)
        if status==0:
            ns_paths = []
            dev = self.dev_name if self.dev_name[-2]!='n' else self.dev_name[:-2]
            for i in range(0, 4096, 4):
                this_byte = result.raw[i]
                if this_byte == 0:
                    break
                ns_paths.append(dev+'n'+str(this_byte))
            return 0, ns_paths
        else:
            return 1, "ERROR"
        
        
            

        return self.ret_status
    
    def submit_passthru(self, nvme_cmd, verify_rsp=False, async_run=False):
        print("LIBNVME submit passthru being sent")
        

        command = nvme_cmd.cmd.generic_command
        nvme_cmd.cmd.generic_command.dptr.sgl.data_len = 4096
        nvme_cmd.cmd.generic_command.dptr.sgl.addr = nvme_cmd.buff
        
        status, error = self.nvme_open()
        if status!=0:
            return status, error
        
        if 0 <= command.cdw0.OPC <= 0x0D:
            #Admin Command
        
            # Prototype definitions
            libnvme_submit_admin_passthru = self.libnvme.nvme_submit_admin_passthru
            libnvme_submit_admin_passthru.argtypes = [ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
            libnvme_submit_admin_passthru.restype = ctypes.c_int32
            print("Structure passed to libnvme is at address ", hex(command.dptr.sgl.addr))
            
            self.ret_status = libnvme_submit_admin_passthru(self.device_descriptor, ctypes.addressof(command), None)
            if self.ret_status!=0:
                print("Command execution unsuccessful: ", self.ret_status)
            return self.ret_status
        
    def connect_dev_in_progress(self):
        

        # r: NVME_ROOT = NVME_ROOT()
        # h: NVME_HOST = NVME_HOST()
        # c: NVME_CTRL = NVME_CTRL()

        cfg = NVME_FABRICS_CONFIG()

        # void nvmf_default_config(struct nvme_fabrics_config *cfg);
        libnvme_nvmf_default_config = self.libnvme.nvmf_default_config
        libnvme_nvmf_default_config.argtypes = [ctypes.POINTER(NVME_FABRICS_CONFIG)]
        libnvme_nvmf_default_config.restype = None

        # nvme_root_t nvme_scan(const char *config_file);
        libnvme_nvme_scan = self.libnvme.nvme_scan
        libnvme_nvme_scan.argtypes = [ctypes.c_char_p]
        libnvme_nvme_scan.restype = ctypes.POINTER(NVME_ROOT)
        
        # nvme_host_t nvme_default_host(nvme_root_t r);
        libnvme_nvme_default_host = self.libnvme.nvme_default_host
        libnvme_nvme_default_host.argtypes = [ctypes.POINTER(NVME_ROOT)]
        libnvme_nvme_default_host.restype = ctypes.POINTER(NVME_HOST)

        # nvme_ctrl_t nvme_create_ctrl(nvme_root_t r,
        #         const char *subsysnqn, const char *transport,
        #         const char *traddr, const char *host_traddr,
        #         const char *host_iface, const char *trsvcid);
        libnvme_nvme_create_ctrl = self.libnvme.nvme_create_ctrl
        libnvme_nvme_create_ctrl.argtypes = [ctypes.POINTER(NVME_ROOT)]+[ctypes.c_char_p]*6
        libnvme_nvme_create_ctrl.restype = ctypes.POINTER(NVME_CTRL)

        # int nvmf_add_ctrl(nvme_host_t h, nvme_ctrl_t c,
        #       const struct nvme_fabrics_config *cfg);
        libnvme_nvmf_add_ctrl = self.libnvme.nvmf_add_ctrl
        libnvme_nvmf_add_ctrl.argtypes = [ctypes.POINTER(NVME_HOST), ctypes.POINTER(NVME_CTRL), ctypes.POINTER(NVME_FABRICS_CONFIG)]
        libnvme_nvmf_add_ctrl.restype = ctypes.c_int

        # int nvmf_get_discovery_log(nvme_ctrl_t c, struct nvmf_discovery_log **logp,
        #         int max_retries);
        libnvme_nvmf_get_discovery_log = self.libnvme.nvmf_get_discovery_log
        libnvme_nvmf_get_discovery_log.argtypes = [ctypes.POINTER(NVME_CTRL), ctypes.POINTER(ctypes.POINTER(NVMF_DISCOVERY_LOG)), ctypes.c_int]
        libnvme_nvmf_get_discovery_log.restype = ctypes.c_int

        # int nvme_disconnect_ctrl(nvme_ctrl_t c);
        libnvme_nvme_disconnect_ctrl = self.libnvme.nvme_disconnect_ctrl
        libnvme_nvme_disconnect_ctrl.argtypes = [ctypes.POINTER(NVME_CTRL)]
        libnvme_nvme_disconnect_ctrl.restype = ctypes.c_int        

        # void nvme_free_ctrl(struct nvme_ctrl *c);
        libnvme_nvme_free_ctrl = self.libnvme.nvme_free_ctrl
        libnvme_nvme_free_ctrl.argtypes = [ctypes.POINTER(NVME_CTRL)]
        libnvme_nvme_free_ctrl.restype = None 

        # void nvme_free_tree(nvme_root_t r);
        libnvme_nvme_free_tree = self.libnvme.nvme_free_tree
        libnvme_nvme_free_tree.argtypes = [ctypes.POINTER(NVME_ROOT)]
        libnvme_nvme_free_tree.restype = None        

        
        libnvme_nvmf_default_config(ctypes.byref(cfg))
        print(cfg.ctrl_loss_tmo)

        r = libnvme_nvme_scan(None)
        h = libnvme_nvme_default_host(r)
        if not h:
            print("Failed to allocate memory to host")
        nqn = "nqn.2023-01.com.samsung.semiconductor:665e905a-bfde-11d3-01aa-a8a159fba2e6_1_1"# NVME_DISC_SUBSYS_NAME
        c = libnvme_nvme_create_ctrl(r, nqn.encode(), "tcp".encode() ,"10.0.0.220".encode() ,None , None, "1153".encode())
        # c = libnvme_nvme_create_ctrl(r, nqn.encode(), "tcp".encode() ,"10.0.0.220".encode() ,None , None, "1153".encode())
        
        if not c:
            print("Failed to allocate memory to ctrl")
        print("DBG")

        status = libnvme_nvmf_add_ctrl(h, c, ctypes.byref(cfg))
        print("DBG")
        if status<0:
            print("No controller found")
        print("END")
        #temp = NVMF_DISCOVERY_LOG()
        # log = NVMF_DISCOVERY_LOG()
        # status = libnvme_nvmf_get_discovery_log(c, ctypes.byref(log), 4)
        # libnvme_nvme_disconnect_ctrl(c)
        # libnvme_nvme_free_ctrl(c)

        # print(status)

    def get_response(self, nvme_cmd):
        
        response = nvme_cmd.rsp.response
        response.sf.SC = self.ret_status
        response.DNR = 0
        response.sf.M = 0
        response.sf.CRD = 0
        response.sf.SCT = 0
        response.sf.SC = 0



if __name__ == '__main__':
    # obj = NVMePassthruCmd()
    # obj  = GenericCommand()
    # print(ctypes.sizeof(obj))

    obj = Libnvme("/dev/nvme2")
    # nvme_cmd = NVMeCommandLib("nvme-cli").get_identify_cmd()
    # identify_data_structure = IdentifyControllerData()

    # nvme_cmd.cmd.generic_command.cdw0.OPC = 0x06
    # nvme_cmd.cmd.generic_command.cdw10.raw = 0x01 #identify CONTROLLER
    # nvme_cmd.cmd.generic_command.dptr.sgl.data_len = 4096
    # nvme_cmd.cmd.generic_command.dptr.sgl.addr = ctypes.addressof(identify_data_structure)

    # status = obj.submit_passthru(nvme_cmd)
    # status, paths = obj.submit_list_ns_cmd()
    # print(paths)  
    obj.connect_dev_in_progress()   
