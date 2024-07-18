# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

"""
Command Library.

Library for maintaing commands supported by framework. Provides functions for
retrieving command structures and command utilities.
"""
from lib.structlib.nvme_struct_main_lib import NVMeCommand
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from utils.logging_module import logger

class NVMeCommandLib:
    """Initialize attributes

        Args:
            app_name (str): Name of application to use
            dev_name (str, optional): Device to use. Defaults to None.
    """

    def __init__(self, app_name, dev_name=None) -> None:
        """ Constructor """
        self.dev_name = dev_name
        self.app_name = app_name.lower()
        if app_name.lower() == "nvme-cli" or app_name.lower() == "nvmecli":
            pass  # self.app = NVMeCLILib(dev_name)
        elif app_name.lower() == "libnvme":
            pass  # self.app = Libnvme(dev_name)
        else:
            pass

    def get_nvme_cmd(self):
        """Retrieve the main NVMeCommand Structure

        Returns:
            NVMeCommand: Object of the NVMeCommand class which represents a C structure
        """
        nvme_cmd = NVMeCommand()

        logger.trace("nvme_cmd returned from Commands Lib")
        return nvme_cmd

    def get_identify_cmd(self):
        """Retrieves the main NVMeCommand Structure with the required fields set for making
            it an identify command

        Returns:
            NVMeCommand: Structure for identify command.
        """
        nvme_cmd = self.get_nvme_cmd()
        nvme_cmd.buff_size = 4096
        nvme_cmd.cmd.identify_cmd.cdw0.OPC = 0x06
        nvme_cmd.cmd.identify_cmd.NSID = 0

        logger.trace("nvme_cmd returned from Commands Lib")
        return nvme_cmd

    def get_identify_controller_cmd(self):
        """Retrieves the main NVMeCommand Structure with the required fields set for making
            it an identify controller command

        Returns:
            NVMeCommand: Structure for identify controller command.
        """
        nvme_cmd = self.get_nvme_cmd()
        nvme_cmd.buff_size = 4096
        nvme_cmd.cmd.identify_cmd.cdw0.OPC = 0x06
        nvme_cmd.cmd.identify_cmd.NSID = 0

        # Making it identify-controller command
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0x01

        logger.trace("nvme_cmd returned from Commands Lib")
        return nvme_cmd

    def get_property_get_cmd(self):
        """Retrieves the main NVMeCommand Structure with the required fields set for making
            it a fabric Property Get command

        Returns:
            NVMeCommand: Structure for Property Get command.
        """
        nvme_cmd = self.get_nvme_cmd()

        nvme_cmd.cmd.generic_command.cdw0.OPC = 0x7f
        nvme_cmd.cmd.generic_command.NSID = 0x04

        logger.trace("nvme_cmd returned from Commands Lib")

        return nvme_cmd
    
    def get_property_set_cmd(self):
        """Retrieves the main NVMeCommand Structure with the required fields set for making
            it a fabric Property Set command

        Returns:
            NVMeCommand: Structure for Property Set command.
        """
        nvme_cmd = self.get_nvme_cmd()
        nvme_cmd.cmd.generic_command.cdw0.OPC = 0x7f
        nvme_cmd.cmd.generic_command.NSID = 0x00

        logger.trace("nvme_cmd returned from Commands Lib")

        return nvme_cmd
    
    def get_get_log_cmd(self, log_id, log_len):
        """Retrieves the main NVMeCommand Structure with the required fields set for making
            it a Get Log command

        Returns:
            NVMeCommand: Structure for Get Log command.
        """
        nvme_cmd = self.get_nvme_cmd()
        nvme_cmd.cmd.generic_command.cdw0.OPC = 0x02
        nvme_cmd.cmd.generic_command.NSID = 0xFFFFFFFF  

        upper = 0
        n_dwords = log_len // 4 - 1
        if n_dwords > 0xFFFF:
            upper = n_dwords >> 16
        lower = n_dwords & 0x0000FFFF

        nvme_cmd.cmd.generic_command.cdw10.raw = (lower << 16) | (log_id & 0xFFFF)
        nvme_cmd.cmd.generic_command.cdw11.raw = upper & 0xFFFF
        nvme_cmd.buff_size = log_len

        logger.trace("nvme_cmd returned from Commands Lib")

        return nvme_cmd
    
    def get_get_features_cmd(self, feature_id=None):
        """Retrieves the main NVMeCommand Structure with the required fields set for making
            it a Get Features command

        Returns:
            NVMeCommand: Structure for Get Features command.
        """
        nvme_cmd = self.get_nvme_cmd()
        nvme_cmd.cmd.generic_command.cdw0.OPC = 0x0A
        nvme_cmd.cmd.generic_command.NSID = 0xFFFFFFFF  

        if feature_id:
            nvme_cmd.cmd.generic_command.cdw10.raw = feature_id
        
        nvme_cmd.buff_size = 0
        
        logger.trace("nvme_cmd returned from Commands Lib")

        return nvme_cmd
    
    def get_read_cmd(self, feature_id=None):
        """Retrieves the main NVMeCommand Structure with the required fields set for making
            it a Read command

        Returns:
            NVMeCommand: Structure for Read command.
        """
        nvme_cmd = self.get_nvme_cmd()
        nvme_cmd.cmd.generic_command.cdw0.OPC = 0x02
        nvme_cmd.cmd.generic_command.NSID = 1 

        # nvme_cmd.buff_size = 512

        # nvme_cmd.cmd.generic_command.dptr.sgl.data_len = nvme_cmd.buff_size
        # nvme_cmd.cmd.generic_command.dptr.sgl.addr = nvme_cmd.buff
        
        logger.trace("nvme_cmd returned from Commands Lib")

        return nvme_cmd
