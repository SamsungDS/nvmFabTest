# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-2-Clause

""" 
NVMe-CLI interface library.

Library that provides an interface for interacting with NVMe devices
using the nvme-cli tool.
This library is designed to be used in the framework that requires interaction
with NVMe devices, and it abstracts the complexities of dealing with the cli
commands and responses.
"""
import ctypes
import sys
sys.path.insert(1, './')
import subprocess
from src.macros import *
from utils.logging_module import logger
from lib.structlib.nvme_struct_main_lib import NVMeCmdStruct
import re
import os


class NVMeCLILib():

    def __init__(self, dev_path=None) -> None:
        """Initialize attributes for the CLI Library

        Args:
            dev_path (str, optional): Device path to which commands need to be sent.
                Defaults to None.
        """
        self.version = ""
        self.dev_version = ""
        self.app_version = ""
        self.app_path = ""
        self.data_buffer = ""
        self.dev_path = dev_path
        self.command = None
        self.err_code = 0
        self.nvme_list = []
        self.subsys_list = []

    @staticmethod
    def mapping(value, start, end):
        """ Extracts a subset of bits from a given integer value

        Args:
            value (int): The integer value from which bits are to be extracted.
            start (int): The starting postion of the subset of bits to be extracted.
            end (int): The ending position (exclusive) of the subste of bits to be extracted.

        Returns:
            int: The extracted subset of bits as an integer.
        """
        mask = (1 << end - start) - 1
        return (value >> start) & mask

    def execute_cmd(self, command, async_run=False):
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

        if not async_run:   

            self.stdout, self.stderr = process.communicate()
            self.ret_code = process.returncode

            if len(self.stderr) != 0 and self.ret_code != 0:
                logger.warning(f"-- -- Command execution failed: {self.stderr[:self.stderr.find(b'\n')]}")
                return self.ret_code
            logger.success("-- -- Command execution success")
            return 0
        
        return process

    def get_app_version(self):
        """Retrieves the version of the nvme-cli installation

        Returns:
            str: nvme-cli version
        """
        cmd = 'nvme version'
        self.execute_cmd(cmd)
        version = str(self.stdout)
        version = version.split(" ")
        return version[2].strip("\n")

    def get_driver_version(self):
        """Retrieves version of the NVMe Driver

        Returns:
            str: driver version
        """
        cmd = ['modinfo nvme | grep -i version']
        self.execute_cmd(cmd)

        version = str(self.stdout.decode().split("\n")[0])
        version = version.split(":")
        return "NVMe" + str(version[1])

    def get_app_path(self):
        """Retrieves the path of the nvme-cli installation

        Returns:
            str: path
        """
        cmd = ['which nvme']
        self.execute_cmd(cmd)

        return self.stdout.decode()

    def get_response(self, nvme_cmd, rsp=None):
        """Parse the response and fill the CQE structure

        Args:
            nvme_cmd: Command object to fill response in
            rsp (bytes, optional): Manually provide response bytes, else takes the
                previously executed commands stdout. Defaults to None.

        Returns:
            bool: Indicates success or failure
        """
        # nvme_cmd.rsp.response = nvme_cmd.rsp.response
        try:
            if self.ret_code != 0:
                completion_val = list(
                    bytes(rsp if rsp else self.stderr).decode('ascii').split(":"))
                val = re.findall(r'\((.*?)\)', completion_val[-1])
                src = int(val[0], 16)
                nvme_cmd.rsp.response.sf.DNR = NVMeCLILib.mapping(src, 14, 15)
                nvme_cmd.rsp.response.sf.M = NVMeCLILib.mapping(src, 13, 14)
                nvme_cmd.rsp.response.sf.CRD = NVMeCLILib.mapping(src, 11, 13)
                nvme_cmd.rsp.response.sf.SCT = NVMeCLILib.mapping(src, 8, 11)
                nvme_cmd.rsp.response.sf.SC = NVMeCLILib.mapping(src, 0, 8)
            else:
                nvme_cmd.rsp.response.sf.DNR = 0
                nvme_cmd.rsp.response.sf.M = 0
                nvme_cmd.rsp.response.sf.CRD = 0
                nvme_cmd.rsp.response.sf.SCT = 0
                nvme_cmd.rsp.response.sf.SC = 0
        except Exception as e:
            logger.exception(e)
        return True

    def get_passthru_result(self):
        return self.stderr[-11:-1].decode() if b"Success" in self.stderr else None

    def get_nqn_from_discover(self, response: bytes, index: int):
        """
        Extracts the NQN (subnqn) from the discovery response thorugh cli.

        Args:
            response (bytes): The discovery response as bytes.
            index (int): The index of the NQN to extract if multiple NQNs are present.

        Returns:
            str: The extracted NQN.
        """
        response = response.decode()
        occurences = [m.start() for m in re.finditer('subnqn', response)]
        index = 0 if len(occurences) == 1 else index
        start = 7 + occurences[index]
        end = response.find('\n', start)
        nqn = response[start:end].strip()
        return nqn

    def prepare_admin_passthru_cmd(self, command: NVMeCmdStruct):
        """
        Prepares the admin passthru command for execution by laying out the dwords.

        Args:
            command: The command object containing the NVMe structure for the
                admin passthru command.

        Returns:
            The formatted command string for executing the admin passthru command.
        """
        opcode = command.cdw0.OPC
        nsid = command.NSID
        cmd_base = "nvme"
        cmd = f"{cmd_base} admin-passthru {self.dev_path} --opcode={opcode} -n {nsid}"
        cmd = f"{cmd} --cdw2={command.cdw2.raw} --cdw3={command.cdw3.raw}"
        cmd = f"{cmd} --cdw10={command.cdw10.raw} --cdw11={command.cdw11.raw}"
        cmd = f"{cmd} --cdw12={command.cdw12.raw} --cdw13={command.cdw13.raw}"
        cmd = f"{cmd} --cdw14={command.cdw14.raw} --cdw15={command.cdw15.raw}"

        return cmd

    def prepare_io_passthru_cmd(self, command: NVMeCmdStruct):
        """
        Prepares the io passthru command for execution by laying out the dwords.

        Args:
            command: The command object containing the NVMe structure for the
                io passthru command.

        Returns:
            The formatted command string for executing the io passthru command.
        """
        opcode = command.cdw0.OPC
        nsid = command.NSID
        cmd_base = "nvme"
        cmd = f"{cmd_base} io-passthru {self.dev_path} --opcode={opcode} --namespace-id={nsid}"
        cmd = f"{cmd} --cdw2={command.cdw2.raw} --cdw3={command.cdw3.raw}"
        cmd = f"{cmd} --cdw10={command.cdw10.raw} --cdw11={command.cdw11.raw}"
        cmd = f"{cmd} --cdw12={command.cdw12.raw} --cdw13={command.cdw13.raw}"
        cmd = f"{cmd} --cdw14={command.cdw14.raw} --cdw15={command.cdw15.raw}"

        return cmd
    
    def submit_discover_cmd(self, transport, address, svcid, hostnqn=None):
        """
        Submit a discover command to the NVMe device.

        Args:
            transport: The transport type.
            address: The address of the NVMe device.
            svcid: The service ID of the NVMe device.

        Returns:
            Tuple[int, bytes]: A tuple containing the status code and the stdout or stderr.
        """
        cmd_base = "nvme"
        cmd = f"{cmd_base} discover"
        cmd = f"{cmd} -t {transport}"
        cmd = f"{cmd} -a {address}"
        cmd = f"{cmd} -s {svcid}"

        if hostnqn:
            cmd = f"{cmd} -q {hostnqn}"
        status = self.execute_cmd(cmd)
        if status == 0:
            return 0, self.stdout
        else:
            return status, self.stderr

    def submit_list_subsys_cmd(self):
        """
        Submits a list-subsys command with stdout in json format. 
        If successful, the stdout is returned in the tuple.

        Args:
            None. 

        Returns:
            Tuple[int, bytes]: A tuple containing the status code and the stdout or stderr.

        """
        cmd_base = "nvme"
        cmd = f"{cmd_base} list-subsys -o json"
        status = self.execute_cmd(cmd)
        if status == 0:
            return status, self.stdout
        else:
            return status, self.stderr
        
    def get_device_lba_size(self, dev=None):
        """
        Submits an id-ns command to retrieve to calculate the block size. 

        Args:
            str: Device path whose block size is to be computed.  

        Returns:
            int: The block size. -1 if error.

        """
        if not dev:
            dev = self.dev_path

        if not re.match(r"/dev/nvme[0-9]+n[0-9]+", dev):
            dev = dev + 'n1'

        cmd_base = "nvme"
        cmd = f"{cmd_base} id-ns {dev}"
        status = self.execute_cmd(cmd)
        if status != 0:
            return -1
        else:
            res = self.stdout.decode()
            l = res.find("lbads")
            r = res.find("rp:")
            res = res[l+6:r-1].strip()            
            return 2**int(res)

    def submit_list_ns_cmd(self):
        """
        Submits a list namespace (list-ns) command.
        Forms the absolute paths to the block devices of each namespace.

        Args:
            None. 

        Returns:
            Tuple[int, List[str] | bytes]:
            - If execution successful, tuple contains status code and list of
                absolute namespace paths.
            - If execution fails, tuple contains status code and stderr.
        """
        cmd_base = "nvme"
        cmd = f"{cmd_base} list-ns"
        cmd = f"{cmd} {self.dev_path}"
        status = self.execute_cmd(cmd)
        if status == 0:
            ns_paths = []
            lines = self.stdout.decode().splitlines()
            for i in range(len(lines)):
                ns_paths.append(self.dev_path+'n' +
                                chr(ord(lines[i][lines[i].find(']')-1])+1))
            return status, ns_paths
        else:
            return status, self.stderr

    def submit_admin_passthru(self, nvme_cmd, verify_rsp=True, async_run=False):
        """
        Submit admin passthru command to the NVMe device.

        Args:
            nvme_cmd: The NVMe command object to be submitted. The "NVMeCmdStruct" 
                will be utilised from "nvme_cmd.cmd" and the reponse is moved to memory
                specified in "nvme_cmd.buff".
            verify_rsp: Flag indicating whether to verify the response. (TBD)
            async_run: Flag indicating whether to run the command asynchronously. (TBD)

        Returns:
            int: Status Code of the command execution.
        """
        command = nvme_cmd.cmd.generic_command
        response = nvme_cmd.rsp.response
        data_len = nvme_cmd.buff_size

        if 0 <= command.cdw0.OPC <= 0x0D:
            # Admin Command
            cmd = self.prepare_admin_passthru_cmd(command)
            cmd = f"{cmd} --data-len={data_len} -r -b"
            ret_status = self.execute_cmd(cmd, async_run=async_run)

            if async_run:
                return ret_status
            
            if ret_status != 0:
                logger.warning("Command execution unsuccessful: ", ret_status)
                return ret_status

            if verify_rsp:
                # self.validate_response()
                # raise Exception("Response invalid")
                pass

            if not response:
                logger.warning("Empty response ")
                return ret_status

            if data_len != 0:
                ctypes.memmove(nvme_cmd.buff, self.stdout, data_len)

            return 0

        if command.cdw0.OPC == 0x7f:
            # Fabric Command
            cmd = self.prepare_admin_passthru_cmd(command)
            cmd = f"{cmd} -r"
            ret_status = self.execute_cmd(cmd, async_run=async_run)

            if ret_status != 0:
                logger.warning("Command execution unsuccessful: ", ret_status)
                return ret_status

            if verify_rsp:
                # self.validate_response()
                # raise Exception("Response invalid")
                pass

            if not response:
                logger.warning("Empty response ")
                return ret_status

            if command.NSID == 0x04:
                # Parse Property Get response
                value = int(str(self.stderr[-9:-1])[2:-1], 16)
                ctypes.memmove(nvme_cmd.buff, value.to_bytes(8, 'little'), 8)

            return 0
        
    def submit_io_passthru(self, nvme_cmd, verify_rsp=True, async_run=False):
        """
        Submit io passthru command to the NVMe device.

        Args:
            nvme_cmd: The NVMe command object to be submitted. The "NVMeCmdStruct" 
                will be utilised from "nvme_cmd.cmd" and the reponse is moved to memory
                specified in "nvme_cmd.buff".
            verify_rsp: Flag indicating whether to verify the response. (TBD)
            async_run: Flag indicating whether to run the command asynchronously. (TBD)

        Returns:
            int: Status Code of the command execution.
        """
        command = nvme_cmd.cmd.generic_command
        response = nvme_cmd.rsp.response
        data_len = nvme_cmd.buff_size

        if command.cdw0.OPC == 0x01:    
            os.mkdir(TEMP_DIR) if not os.path.exists(TEMP_DIR) else None
            input_file = f'{TEMP_DIR}/write_001.txt'
            
            with open(input_file, 'wb') as f:
                f.write(ctypes.string_at(nvme_cmd.buff, nvme_cmd.buff_size))

            cmd = self.prepare_io_passthru_cmd(command)
            cmd = f"{cmd} --data-len={data_len} --input-file={input_file} -w"
            ret_status = self.execute_cmd(cmd, async_run=async_run)
        
        else:
            cmd = self.prepare_io_passthru_cmd(command)
            cmd = f"{cmd} --data-len={data_len} -r -b"
            ret_status = self.execute_cmd(cmd, async_run=async_run)
            
            if data_len != 0:
                ctypes.memmove(nvme_cmd.buff, self.stdout, data_len)


        if ret_status != 0:
            logger.warning("Command execution unsuccessful: ", ret_status)
            return ret_status

        if verify_rsp:
            # self.validate_response()
            # raise Exception("Response invalid")
            pass

        if not response:
            logger.warning("Empty response ")
            return ret_status
        
        return 0

    def submit_connect_cmd(self, transport, address, svcid, nqn, kato=None,
                           duplicate=False, hostnqn=None, hostid=None, nr_io_queues=None,
                           dhchap_host=None, dhchap_ctrl=None):
        """
        Submit a connect command to establish a connection with an NVMe fabric device.

        Args:
            transport (str): The transport type for the connection.
            address (str): The address of the NVMe device.
            svcid (str): The service ID for the connection.
            nqn (str): The NVMe Qualified Name (NQN) of the device.
            kato (int, optional): Keep Alive Timeout (KATO) value in milliseconds.
            duplicate (bool, optional): Flag indicating whether to allow duplicate
                connection.
            hostnqn (str, optional): The NVMe Qualified Name (NQN) of the host.
            hostid (str, optional): The host ID for the connection.
            nr_io_queues (int, optional): The number of I/O queues to be used.

        Returns:
            Tuple[int, bytes]: A tuple containing the status code and the stdout or stderr.
        """
        cmd_base = "nvme"
        cmd = f"{cmd_base} connect"
        cmd = f"{cmd} -t {transport}"
        cmd = f"{cmd} -a {address}"
        cmd = f"{cmd} -s {svcid}"
        cmd = f"{cmd} -n {nqn}"
        if kato != None:
            cmd = f"{cmd} -k {kato}"
        if hostnqn != None:
            cmd = f"{cmd} -q {hostnqn}"
        if hostid != None:
            cmd = f"{cmd} -I {hostid}"
        if nr_io_queues != None:
            cmd = f"{cmd} -i {nr_io_queues}"
        if dhchap_host:
            cmd = f"{cmd} -S {dhchap_host}"
        if dhchap_ctrl:
            cmd = f"{cmd} -C {dhchap_ctrl}"
        if duplicate:
            cmd = f"{cmd} -D"

        status = self.execute_cmd(cmd)

        alreadyConnected = self.stderr.decode().strip().endswith(
            "Operation already in progress")

        if status == 0:
            ind = self.stdout.decode().find(':')
            return 0, "/dev/"+self.stdout[ind+2:-1].decode()
        else:
            if alreadyConnected:
                return status, "Already connected to device."
            return status, self.stderr

    def submit_disconnect_cmd(self, nqn=None, device_path=None):
        """
        Submits a disconnect command to the NVMe fabric device.
        If no arguments are given, then it will disconnect the dev_name attribute
            stored in the object. 
        If dev_name is not set, then raise error.

        Args:
            nqn (str, optional): The NQN of the device to disconnect.
            device_path (str, optional): The path of the device to disconnect.  

        Returns:
            Tuple[int, bytes]: A tuple containing the status code and the stdout or stderr.

        Raises:
            NameError: If device path is not in correct format.
        """
        cmd_base = "nvme"
        cmd = f"{cmd_base} disconnect"
        if nqn:
            cmd = f"{cmd} -n {nqn}"
        elif device_path:
            if not re.match(r"\A/dev/nvme[0-9]+\Z", device_path):
                raise NameError(
                    f"Cannot disconnect this device: {device_path}")
            cmd = f"{cmd} -d {device_path}"
        else:
            if not re.match(r"\A/dev/nvme[0-9]+\Z", self.dev_path):
                raise NameError(
                    f"Cannot disconnect this device: {self.dev_path}")
            cmd = f"{cmd} -d {self.dev_path}"

        status = self.execute_cmd(cmd)

        if status == 0:
            return status, self.stdout
        else:
            return status, self.stderr
