
import ctypes

import sys 
sys.path.insert(1, "/root/nihal223/nvmfabtest/lib/structlib")

from struct_base_lib import *
from struct_admin_cmd_lib import *
from struct_nvm_cmd_lib import *
from struct_admin_data_lib import *


class NVMeCmdStruct(ctypes.Union):
    _pack_ = 1
    _fields_ = [("generic_command", GenericCommand),
                ("delete_io_subq_cmd", GenericCommand),         # OPC 0x0
                ("create_io_subq_cmd", GenericCommand),         # OPC 0x1
                ("get_log_page_cmd", GetLogPageCommand),        # OPC 0x2
                ("delete_io_comq_cmd", GenericCommand),         # OPC 0x4
                ("create_io_comq_cmd", GenericCommand),         # OPC 0x5
                ("identify_cmd", IdentifyCommand),              # OPC 0x6
                ("abort_cmd", GenericCommand),                  # OPC 0x8
                ("set_feature_cmd", GenericCommand),            # OPC 0x9
                ("get_feature_cmd", GenericCommand),            # OPC 0xA
                ]
    
class NVMeRspStruct(ctypes.Union): 
    _pack_ = 1
    _fields_ = [("response", Response),
                ("identify_rsp", Response)]
    
class NVMeDataStruct(ctypes.Union): 
    _pack_ = 1
    _fields_ = [("identify_ctrl_data", IdentifyControllerData)]


class NVMeCommand(ctypes.Structure): 
    _pack_ = 1
    _fields_ = [("cmd", NVMeCmdStruct),         # NVMe Command 
                ("rsp", NVMeRspStruct),         # NVMe Response
                ("buff", ctypes.c_void_p),      # NVMe Data Buffer
                ("buff_size", ctypes.c_uint32),      # NVMe Data Size
                ("timeout_ms", ctypes.c_uint32)  # Command timeout ms
                ]   


if __name__ == '__main__':
    nvme_data = NVMeCommand()
    identify_cmd = nvme_data.cmd.identify_cmd
    identify_rsp = nvme_data.rsp.identify_rsp
    nvme_rsp = NVMeRspStruct()
    data = NVMeDataStruct()
