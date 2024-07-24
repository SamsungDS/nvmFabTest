# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-2-Clause

""" Admin Command Data Structures library """

import ctypes


class NVMSR(ctypes.Structure): #Byte 253
    """Structure representing NVM Enclosure and Storage Device information."""
    # _pack_ = 1
    _fields_ = [("Reserved", ctypes.c_uint8, 6), #bits 7-2 
                ("NVMEE", ctypes.c_uint8, 1), #bit 1 #NVMeEnclosure
                ("NVMESD", ctypes.c_uint8, 1), #bit 0 #NVMeStorageDevice
                ]
    

class VWCI(ctypes.Structure): #Byte 254
    """Structure representing VPD Write Cycle Information."""

    # _pack_ = 1
    _fields_ = [("VWCRV", ctypes.c_uint8, 1), #bit 7 #VPD Write Cycle Remaining Valid
                ("VWCR", ctypes.c_uint8, 7), #bits 6-0 #VPD Write Cycles Remaining
                ]
    

class MEC(ctypes.Structure): #Byte 255
    """Structure representing Management Endpoint Capabilities."""
    
    # _pack_ = 1
    _fields_ = [("Reserved", ctypes.c_uint8, 6), #bits 7-2 
                ("PCIEME", ctypes.c_uint8, 1), #bit 1 #PCIe Port Management Endpoint
                ("SMBUSME", ctypes.c_uint8, 1), #bit 0 #SMBus/I2C Port Management Endpoint
                ]
    

class NVMeManagementInterface(ctypes.Structure): #NVMe MI Figure 136
    """Structure representing NVMe Management Interface."""
    
    # _pack_ = 1
    _fields_ = [("Reserved", ctypes.c_uint32 *13), #B252-240
                ("NVMSR", NVMSR), #B253 #NVM Subsystem Report
                ("VWCI", VWCI), #B254 #VPD Write Cycle Information
                ("MEC", MEC), #B255 #Management Endpoint Capabilities 
                ]
    

class IdentifyControllerData(ctypes.Structure): #Figure 247
    """Structure representing Identify Controller Data."""

    # _pack_ = 1
    _fields_ = [("VID", ctypes.c_uint16),  #B1-0 # PCI Vendor ID            
                ("SSVID", ctypes.c_uint16), #B3-2 # PCI Subsystem Vendor ID 
                ("SN", ctypes.c_char * 20), #B23-04 # Serial Number 
                ("MN", ctypes.c_char * 40), #B63-24 # Model Number 
                ("FR", ctypes.c_char * 8), #B71-64 # Firmware Revision 
                ("RAB", ctypes.c_uint8), #B72 # Recommended Arbitration Burst 
                ("IEEE", ctypes.c_uint8 * 3), #B75-73 # IEEE Organization Unique Identifier
                ("CMIC", ctypes.c_uint8), #B76 # Controller Multi-Path I/O and Namespace Sharing Capabilities
                ("MDTS", ctypes.c_uint8), #B77 # Maximum Data Transfer Size
                ("CNTLID", ctypes.c_uint16), #B79-78 # Controller ID
                ("VER", ctypes.c_uint32), #B83-80 #Version
                ("RTD3R", ctypes.c_uint32), #87-84 #RTD3 Resume Latency
                ("RTD3E", ctypes.c_uint32), #91-88 #RTD3 Entry Latency
                ("OAES", ctypes.c_uint32), #95-92 #Optional Asynchronous Events Supported
                ("CTRATT", ctypes.c_uint32), #99-96 #Controller Attributes
                ("RRLS", ctypes.c_uint16), #101-100 #Read Recovery Levels Supported                
                ("Reserved1", ctypes.c_uint8*9), #110-102 #Reserved
                ("CNTRLTYPE", ctypes.c_uint8), #111 #Controller Type
                ("FGUID", ctypes.c_uint64*2), #127-112 # FRU Globally Unique Identifier
                ("CRDT1", ctypes.c_uint16), #129-128 #Command Retry Delay Time 1
                ("CRDT2", ctypes.c_uint16), #131-130 #Command Retry Delay Time 2
                ("CRDT3", ctypes.c_uint16), #133-132 #Command Retry Delay Time 3
                ("Reserved2", ctypes.c_uint32*106), #239-134 #Reserved
                ("NVMeManagementInterface", NVMeManagementInterface), #255-240 #NVMe Management Interface Identify Controller
                ("OACS", ctypes.c_uint16), #B257-256 #Optional Admin Command Support
                ("ACL", ctypes.c_uint8), #B258 #Abort Command Limit
                ("AERL", ctypes.c_uint8), #B259 #Asynchronous Event Request Limit 
                ("FRMW", ctypes.c_uint8), #B260 #Firmware Updates
                ("LPA", ctypes.c_uint8), #B261 #Log Page Attributes
                ("ELPE", ctypes.c_uint8), #B262 #Error Log Page Entries
                ("NPSS", ctypes.c_uint8), #B263 #Number of Power States Support
                ("AVSCC", ctypes.c_uint8), #B264 #Admin Vendor Specific Command Configuration
                ("APSTA", ctypes.c_uint8), #B265 #Autonomous Power State Transition Attributes
                ("WCTEMP", ctypes.c_uint16), #B267-266 #Warning Composite Temperature Threshold
                ("CCTEMP", ctypes.c_uint16), #B269-268 #Critical Composite Temperature Threshold
                ("MTFA", ctypes.c_uint16), #B271-270 #Maximum Time for Firmware Activation
                ("HMPRE", ctypes.c_uint32), #B275-272 #Host Memory Buffer Preferred Size
                ("HMMIN", ctypes.c_uint32), #B279-276 #Host Memory Buffer Minimum Size
                # Need to define from 280 Byte onwards Page 180 of Fig. 247
                ("Remaining", ctypes.c_uint8 * 3816)
                ]
