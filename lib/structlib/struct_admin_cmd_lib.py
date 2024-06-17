""" Admin Command structures library """

import ctypes
from struct_base_lib import *


class IdentifyCDW10_Struct(ctypes.Structure):
    """
    Structure representing the CDW10 for the Identify Command.
    """
    # _pack_ = 1
    _fields_ = [("CNTID", ctypes.c_uint32, 16),  # Controller Identifier # 16 - 31
                ("Reserved", ctypes.c_uint32, 8), # 8 - 15
                ("CNS", ctypes.c_uint32, 8), # Log Page Identifier # 0 - 7
                ]


class IdentifyCDW11_Struct(ctypes.Structure):
    """
    Structure representing the CDW11 for the Identify Command.
    """
    # _pack_ = 1
    _fields_ = [("Reserved", ctypes.c_uint16),                     # 15 - 31
                ("NVMSETID", ctypes.c_uint16),  # NVM Set identifier # 0 - 15
                ]


class IdentifyCommand(ctypes.Structure):  # Submission Queue Entry Fig 105
    """
    Structure representing the Identify Command.
    """
    # _pack_ = 1
    _fields_ = [("cdw0", CDW0),  # 0 - 3
                ("NSID", ctypes.c_uint32),  # 4 - 7
                ("cdw2", CDW2),  # 8 - 11
                ("cdw3", CDW3),  # 12 - 15
                ("mptr", ctypes.c_uint64),  # 16 - 23
                ("dptr", DPTR),  # 24 - 39
                ("cdw10", CDW10),  # IdentifyCDW10_Struct), # 40 - 43
                ("cdw11", CDW11),  # IdentifyCDW11_Struct), # 44 - 47
                ("cdw12", CDW12),  # 48 - 51
                ("cdw13", CDW13),  # 52 - 55
                ("cdw14", CDW14),  # 56 - 59
                ("cdw15", CDW15),  # 60 - 63
                ]


class GetLogPageCDW10(ctypes.Structure):
    """
    Structure representing the Command DWord 10 for the Get Log Page Command.
    """
    # _pack_ = 1
    _fields_ = [("NUMDL", ctypes.c_uint16),  # Number of Dwords Lower     # 16 - 31
                ("RAE", ctypes.c_uint8, 1),  # Retain Asynchronous Event  # 15
                ("Reserved", ctypes.c_uint8, 3),                        # 12 - 14
                # Log Specific Field         # 8 - 11
                ("LSP", ctypes.c_uint8, 4),
                ("LID", ctypes.c_uint8),  # Log Page Identifier           # 0 - 7
                ]


class GetLogPageCommand(ctypes.Structure):  # Submission Queue Entry
    """
    Structure representing the Get Log Page Command.
    """
    # _pack_ = 1
    _fields_ = [("cdw0", CDW0),  # 0 - 3
                ("NSID", ctypes.c_uint32),  # 4 - 7
                ("cdw2", CDW2),  # 8 - 11
                ("cdw3", CDW3),  # 12 - 15
                ("mptr", ctypes.c_uint64),  # 16 - 23
                ("dptr", DPTR),  # 24 - 39
                ("cdw10", GetLogPageCDW10),  # 40 - 43
                ("cdw11", CDW11),  # 44 - 47
                ("CDW12", CDW12),  # 48 - 51
                ("CDW13", CDW13),  # 52 - 55
                ("CDW14", CDW14),  # 56 - 59
                ("CDW15", CDW15),  # 60 - 63
                ]
