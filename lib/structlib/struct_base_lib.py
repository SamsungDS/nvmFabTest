import ctypes
# NVMe Command Response Structure

class CDW0(ctypes.Structure): # Fig 104
    _pack_ = 1
    _fields_ = [("OPC", ctypes.c_uint8), #Op Code   # 0 - 7  
                ("FUSE", ctypes.c_uint8, 2), # Fused Operation     # 8 - 9
                ("Reserved", ctypes.c_uint8, 4),                   # 10 - 13
                ("PSDT", ctypes.c_uint8, 2),#PRP/SGLforDataTransfer# 14 - 15 
                ("CID", ctypes.c_uint16), # Command Identifier     # 16 - 31
                ]

class PRP(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("PRP1", ctypes.c_uint64), 
                ("PRP2", ctypes.c_uint64),
                ]

class SGL(ctypes.Structure):
    _pack_ = 1
    _fields_ =[ ("addr", ctypes.c_uint64),
                ("metadata_len", ctypes.c_uint32),
                ("data_len", ctypes.c_uint32),
                ]

class DPTR(ctypes.Union):
    _pack_ = 1
    _fields_ = [("prp", PRP),
                ("sgl", SGL),
                ]

class CDW2(ctypes.Union):
    _pack_ = 1
    _fields_ = [("Reserved", ctypes.c_uint32),
                ("raw", ctypes.c_uint32)]

class CDW3(ctypes.Union):
    _pack_ = 1
    _fields_ = [("Reserved", ctypes.c_uint32),
                ("raw", ctypes.c_uint32)]

class CDW10(ctypes.Union):
    _pack_ = 1
    _fields_ = [("raw", ctypes.c_uint32)]

class CDW11(ctypes.Union):
    _pack_ = 1
    _fields_ = [("raw", ctypes.c_uint32)]

class CDW12(ctypes.Union):
    _pack_ = 1
    _fields_ = [("raw", ctypes.c_uint32)]

class CDW13(ctypes.Union):
    _pack_ = 1
    _fields_ = [("raw", ctypes.c_uint32)]

class CDW14(ctypes.Union):
    _pack_ = 1
    _fields_ = [("raw", ctypes.c_uint32)]

class CDW15(ctypes.Union):
    _pack_ = 1
    _fields_ = [("raw", ctypes.c_uint32)]

class GenericCommand(ctypes.Structure): #Submission Queue Entry Fig 105
    _pack_ = 1
    _fields_ = [("cdw0", CDW0), # 0 - 3
                ("NSID", ctypes.c_uint32), # 4 - 7
                ("cdw2", CDW2), # 8 - 11
                ("cdw3", CDW3), # 12 - 15
                ("mptr", ctypes.c_uint64), # 16 - 23
                ("dptr", DPTR), # 24 - 39
                ("cdw10", CDW10), # 40 - 43
                ("cdw11", CDW11), # 44 - 47
                ("cdw12", CDW12), # 48 - 51
                ("cdw13", CDW13), # 52 - 55
                ("cdw14", CDW14), # 56 - 59
                ("cdw15", CDW15)  # 60 - 63
                ]


# NVMe Command Response Structure

class StatusField(ctypes.Structure): 
    _pack_ = 1
    _fields_ = [("DNR", ctypes.c_uint8, 1), # Do Not Retry              #31
                ("M", ctypes.c_uint8, 1), # More                        #30
                ("CRD", ctypes.c_uint8, 2), # Command Retry Delay   #28 - 29
                ("SCT", ctypes.c_uint8, 3), # Status Code Type      #25 - 27
                ("SC", ctypes.c_uint8), # Status Code               #17 - 24
                ]

class CommandSpecific32(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("CommandSpecific32", ctypes.c_uint32),
                ("Reserved", ctypes.c_uint32)
                ]

class CommandSpecific(ctypes.Union):
    _pack_ = 1
    _fields_ = [("command_specific_32", CommandSpecific32),
                ("CommandSpecific64", ctypes.c_uint64),
                ]

class Response(ctypes.Structure): #Completion Queue Entry
    _pack_ = 1
    _fields_ = [("command_specific", CommandSpecific), #DW0-1,  C.S and Reserved 
                ("SQID", ctypes.c_uint16), #SQ Identifier   #DW2 (16 - 31)
                ("SQHD", ctypes.c_uint16), #SQ Head Pointer #DW2 (0 - 15)
                ("sf", StatusField), #Status Field  #DW3 (17-31)
                ("P", ctypes.c_uint8, 1), #Phase Tag             #DW3 (16)
                ("CID", ctypes.c_uint16), #CommandIdentifier #DW3 (0 - 15) 
                ]


