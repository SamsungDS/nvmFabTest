""" Main structures library """

import sys
sys.path.insert(1, "./lib/structlib")
from struct_admin_data_lib import *
from struct_nvm_cmd_lib import *
from struct_admin_cmd_lib import *
from struct_base_lib import *
import ctypes


class NVMeCmdStruct(ctypes.Union):
    """
    Represents the NVMe Command Structure.

    This class defines a union structure that can be used to access different types of NVMe commands.
    Each command type is represented by a different field in the structure.

    Attributes:
        generic_command (GenericCommand): Represents a generic NVMe command.
        delete_io_subq_cmd (GenericCommand): Represents the delete IO submission queue command.
        create_io_subq_cmd (GenericCommand): Represents the create IO submission queue command.
        get_log_page_cmd (GetLogPageCommand): Represents the get log page command.
        delete_io_comq_cmd (GenericCommand): Represents the delete IO completion queue command.
        create_io_comq_cmd (GenericCommand): Represents the create IO completion queue command.
        identify_cmd (GenericLibnvmeCommand): Represents the identify command.
        abort_cmd (GenericCommand): Represents the abort command.
        set_feature_cmd (GenericCommand): Represents the set feature command.
        get_feature_cmd (GenericCommand): Represents the get feature command.
    """
    
    # _pack_ = 1
    _fields_ = [("generic_command", GenericCommand),
                ("delete_io_subq_cmd", GenericCommand),         # OPC 0x0
                ("create_io_subq_cmd", GenericCommand),         # OPC 0x1
                ("get_log_page_cmd", GetLogPageCommand),        # OPC 0x2
                ("delete_io_comq_cmd", GenericCommand),         # OPC 0x4
                ("create_io_comq_cmd", GenericCommand),         # OPC 0x5
                ("identify_cmd", GenericLibnvmeCommand),              # OPC 0x6
                ("abort_cmd", GenericCommand),                  # OPC 0x8
                ("set_feature_cmd", GenericCommand),            # OPC 0x9
                ("get_feature_cmd", GenericCommand),            # OPC 0xA
                ]


class NVMeRspStruct(ctypes.Union):
    """
    Represents the NVMe response structure.

    This class is a ctypes Union that can be used to interpret the response
    data received from an NVMe device. It provides access to different response
    types based on the command being executed.

    Attributes:
        response (Response): The generic response structure.
        identify_rsp (Response): The response structure for identify commands.
    """
    
    # _pack_ = 1
    _fields_ = [("response", Response),
                ("identify_rsp", Response)]


class NVMeDataStruct(ctypes.Union):
    """
    Represents a data structure for NVMe devices.
    """

    # _pack_ = 1
    _fields_ = [("identify_ctrl_data", IdentifyControllerData)]


class NVMeCommand(ctypes.Structure):
    """
    Represents an NVMe Command structure.
    This is the main object which is used for encapsulating all structures.

    Attributes:
        cmd (NVMeCmdStruct): NVMe Command.
        rsp (NVMeRspStruct): NVMe Response.
        buff (ctypes.c_void_p): NVMe Data Buffer.
        buff_size (ctypes.c_uint32): NVMe Data Size.
        timeout_ms (ctypes.c_uint32): Command timeout in milliseconds.
    """
    
    # _pack_ = 1
    _fields_ = [("cmd", NVMeCmdStruct),         # NVMe Command
                ("rsp", NVMeRspStruct),         # NVMe Response
                ("buff", ctypes.c_void_p),      # NVMe Data Buffer
                ("buff_size", ctypes.c_uint32),      # NVMe Data Size
                ("timeout_ms", ctypes.c_uint32)  # Command timeout ms
                ]
