import ctypes


class ConnectCommand(ctypes.Structure): #Submission Queue Connect Command
    '''
    Connect Command Submission Queue Entry
    Figure 19, NVMe Fabric Specification 1.1a
    '''
    _pack_ = 1
    _fields_ = [("OPC", ctypes.c_uint8), # Byte 0
                ("Reserved1", ctypes.c_uint8), # Byte 1
                ("CID", ctypes.c_char * 8), # Bytes 2-3
                ("FCTYPE", ctypes.c_byte), # Bytes 4
                ("Reserved2", ctypes.c_ubyte * 19), # # Bytes 05-23
                ("SGL1", ctypes.c_uint8 * 16), # Bytes 24 - 39
                ("RECFMT", ctypes.c_uint16), # Bytes 40 - 41
                ("QID", ctypes.c_uint16),# Bytes 42 - 43
                ("SQSIZE", ctypes.c_uint16), # Bytes 44 - 45
                ("CATTR", ctypes.c_uint8), # 52 - 55
                ("Reserved3", ctypes.c_uint8), # Byte 47
                ("KATO", ctypes.c_uint32), # Bytes 48 - 51
                ("Reserved4", ctypes.c_uint8 * 12), # Byte 52 - 63
                ]

class ConnectCommandData(ctypes.Structure):
    '''
    Connect Command Data
    Figure 20, NVMe Fabric Specification 1.1a
    '''
    _pack_ = 1
    _fields_ = [("HOSTID", ctypes.c_char * 16), # Bytes 0-15
                ("CNTLID", ctypes.c_uint16), # Byte 16 - 17
                ("Reserved1", ctypes.c_ubyte * 238), # # Bytes 18-255
                ("SUBNQN", ctypes.c_char * 256), # Bytes 256 - 511
                ("HOSTNQN", ctypes.c_char * 256), # Bytes 512 - 767
                ("Reserved2", ctypes.c_uint8 * 256), # Byte 768-1023
                ]


class StatusSuccess(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("CNTLID", ctypes.c_uint16), # Byte 0 - 1
                ("AUTHREQ", ctypes.c_uint16), # Byte 2 - 3
                ]
    
class StatusFailure(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("IPO", ctypes.c_uint16), # Byte 0 - 1
                ("IATTR", ctypes.c_uint8), # Byte 2
                ("Reserved", ctypes.c_uint8), # Byte 3
                ]

class StatusCode(ctypes.Union):
    _pack_ = 1
    _fields_ = [("success", StatusSuccess),
                ("failure", StatusFailure),                
                ]

class ConnectResponse(ctypes.Structure):
    '''
    Connect Command Response
    Figure 21, NVMe Fabric Specification 1.1a
    '''
    _pack_ = 1
    _fields_ = [("status_code", StatusCode), # Byte 0 - 3
                ("Reserved1", ctypes.c_uint32), # Byte 4 - 7
                ("SQHD", ctypes.c_uint16), # Bytes 8-9
                ("Reserved2", ctypes.c_uint16), # Bytes 10-11
                ("CID", ctypes.c_uint16), # Bytes 12-13
                ("STS", ctypes.c_uint16), # Bytes 14-15
                ]