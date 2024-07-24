# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-2-Clause

""" 
System interface library.

Library that provides an interface for runnning system commands.

This library is designed to be used in the framework that requires interaction
with the system for any network, driver or miscellenous requirements.
"""

import sys
sys.path.insert(1, "./")
import subprocess
from utils.logging_module import logger


class SystemLib():
    
    def __init__(self) -> None:
        """
        Initialize attributes for the System Library
        """
        self.stdout = None
        self.stderr = None

    def execute_cmd(self, command):
        """
        Executes the given command and captures the stdout, stderr, and return code.

        Args:
            command (str): The command to be executed.
            async_run (bool, optional): If True, the command will be executed
                asynchronously. Defaults to False.

        Returns:
            int: 0 if the command execution is successful, 1 otherwise.
        """
        logger.info("-- Executing Command: {}", command)
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.stdout, self.stderr = process.communicate()
        self.ret_code = process.returncode

        if len(self.stderr) != 0 and self.ret_code != 0:
            logger.warning(f"-- -- Command execution failed: {self.stderr[:112]}")
            return self.ret_code
        logger.success("-- -- Command execution success")
        return 0

    def get_network_interface(self):
        """
        Submits a system command to retrieve the active
        network interface in use.

        Args: None.

        Returns:
            str: The active network interface name
        """
        cmd = "route | grep \'^default\' | grep -o \'[^ ]*$\'"

        self.execute_cmd(cmd)

        return self.stdout.decode()[:-1]
    
    def set_link(self,  mode: str, iface: str):
        """
        Submits a system command to set the network interface
        down or up. This can simulate a link failure.

        Args:
            mode: String "up" or "down indicating what the link
                should be set to.
            iface: The network interface name whose link is to be set.
                
        Returns:
            int: Status Code of the execution
        """
        cmd = f"ip link set {iface} {mode.strip().lower()}"
        return self.execute_cmd(cmd)
    
    def sleep(self, time: int):
        """
        Submits a system command to sleep/wait for specified seconds.

        Args:
            time: Time to sleep for in seconds
        Returns:
            int: Status Code of the execution
        """

        cmd = f"sleep {time}"
        return self.execute_cmd(cmd)
