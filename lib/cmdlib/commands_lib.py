"""
Command Library.

Library for maintaing commands supported by framework. Provides functions for
retrieving command structures and command utilities.
"""
from lib.structlib.nvme_struct_main_lib import NVMeCommand
from lib.structlib.struct_admin_data_lib import IdentifyControllerData


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
        if app_name.lower() == "nvme-cli":
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
        nvme_cmd.cmd.generic_command.cdw10.raw = 0
        nvme_cmd.cmd.generic_command.cdw11.raw = 0x14

        return nvme_cmd
