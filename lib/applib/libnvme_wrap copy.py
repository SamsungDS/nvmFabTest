import sys
sys.path.insert(1, "/root/nihal223/nvmfabtest")

import os, json, re
from lib.structlib.nvme_struct_main_lib import NVMeCommand, NVMeRspStruct
from utils.logging_module import logger
import ctypes
from lib.applib.nvme_cli_lib import ApplicationLib 
from lib.structlib.struct_admin_data_lib import IdentifyControllerData

class LibnvmeArgs(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("result", ctypes.POINTER(ctypes.c_uint32)), #rr
                ("data", ctypes.c_void_p), #r
                ("args_size", ctypes.c_uint), 
                ("fd", ctypes.c_uint),  #rr
                ("timeout", ctypes.c_uint32), #r
                ("cns", ctypes.c_uint8), #r
                ("csi", ctypes.c_uint8), #r
                ("nsid", ctypes.c_uint32), #r
                ("cntid", ctypes.c_uint16), #r
                ("cns_specific_id", ctypes.c_uint16), #r
                ("uuidx", ctypes.c_uint8), #r
                ]

class Libnvme():
    def __init__(self, dev_path) -> None:
        if re.match(r"\A/dev/nvme[0-9]+(n[0-9]+)?\Z", dev_path):
            self.dev_name = dev_path[5:]
        self.command = None
        self.response = None
        libnvme_path = Libnvme.get_libnvme_path()
        self.libnvme = ctypes.CDLL(libnvme_path)
        self.args = LibnvmeArgs()

    @staticmethod
    def get_libnvme_path():
        f = open("config/ts_config.json")
        ts_config = json.load(f)
        f.close()
        
        #Finding system's libnvme.so file
        if ts_config["libnvme_path"].lower()=="auto":
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
            print(f"Failed to open NVMe device {device_name}. Error code {device_descriptor}")
            return device_descriptor
        else:
            print(f"NVMe device {device_name} opened successfully.")
            self.args.fd = device_descriptor
            return 0

    def nvme_identify(self, args_address):
        # Structure instantiations and identify stuff
        self.identify_data_structure = IdentifyControllerData()
        self.args.data = ctypes.addressof(self.identify_data_structure)
        self.args.args_size = 4096

        # Prototype definitions
        nvme_identify = self.libnvme.nvme_identify
        nvme_identify.argtypes = [ctypes.c_void_p]
        nvme_identify.restype = ctypes.c_int

        #Run from libnvme C function
        status = nvme_identify(args_address)

        if status != 0:
            print(f"Failed identify command to NVMe device with struct at {args_address}.")
        else:
            print("Identify data success: Response should be \
in memory location pointed by the address \
self.args->data: ", hex(self.args.data))
        return status

    def submit_identify_controller(self, verify_rsp=False, async_run=False):
        self.args.cns = 0x01 #identify CONTROLLER

        status = self.nvme_open()
        if status!=0:
            return status
        args_addr = ctypes.addressof(self.args)
        print("Structure passed to libnvme is at address ", hex(args_addr))
        
        return self.nvme_identify(args_addr)
        

    def get_response(self):  
        print("SN: ", self.identify_data_structure.SN.decode())
        return self.identify_data_structure


if __name__ == '__main__':
    obj = Libnvme("/dev/nvme2")
    status = obj.submit_identify_controller()
    if status==0:
        obj.get_response()