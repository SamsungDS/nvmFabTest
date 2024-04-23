import sys 
sys.path.insert(1, "/root/nihal223/nvmfabtest")

import re
from lib.structlib.nvme_struct_main_lib import NVMeRspStruct
from utils.logging_module import logger
import subprocess
import ctypes

class ApplicationLib():
    def __init__(self, dev_path) -> None:
        self.version = ""
        self.dev_version = ""
        self.cntrl = ""

def bit_combining(value, pos, limit):
        dif = limit-pos
        mask = (1 << dif)-1
        if pos == 0:
            out = (value & mask)
        else:
            out = (value >> pos) & mask
        return out


class NVMeCLILib(ApplicationLib):
    def __init__(self, dev_path='') -> None:
        super(NVMeCLILib, self).__init__(dev_path)
        self.version = ""
        self.dev_version = ""
        self.app_version = ""
        self.app_path = ""
        self.data_buffer = ""
        # self.dev = dev
        self.dev_path = dev_path
        self.command = None
        self.response = None
        self.err_code = 0
        self.nvme_list = []
        self.subsys_list = []

    def execute_cmd(self, command, async_run=False):
        print("-- Executing Command: ", command)
        process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.stdout, self.stderr = process.communicate()
        self.ret_code = process.returncode
        if len(self.stderr) != 0:
            print("-- -- Command execution failed")
            return 1
        print("-- -- Command execution success")
        return 0

    def get_app_details(self):
        """
        """
        self.app_version = self.get_app_version()
        self.dev_version = self.get_dev_version()
        self.app_path = self.get_app_path()

    def get_app_version(self):
        """
        """
        cmd = 'nvme version'
        self.execute_cmd(cmd)
        version = str(self.app_buffer)
        version = version.split(" ")
        return version[2].strip("\n")

    def get_driver_version(self):
        """
        """
        cmd = ['modinfo nvme | grep -i version']
        self.execute_cmd(cmd)

        version = str(self.stdout.readlines()[0])
        version = version.split(":")
        return "NVMe" + str(version[1])

    def get_app_path(self):
        """
        """
        cmd = ['whereis nvme cli']
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        version = str(proc.stdout.readlines()[0])
        version = version.split(":")
        return version[1]
    
    def get_response(self, nvme_cmd):
        """
        """
        # print(self.stderr)
        self.response = nvme_cmd.rsp.response
        try:
            if self.ret_code != 0:
                completion_val = list(bytes(self.stderr).decode('ascii').split(":"))
                val = re.findall(r'\((.*?)\)', completion_val[-1])
                self.response.sf.DNR = bit_combining(int(val[0], 16), 14, 15)
                self.response.sf.M = bit_combining(int(val[0], 16), 13, 14)
                self.response.sf.CRD = bit_combining(int(val[0], 16), 11, 13)
                self.response.sf.SCT = bit_combining(int(val[0], 16), 8, 11)
                self.response.sf.SC = bit_combining(int(val[0], 16), 0, 8)
            else:
                self.response.DNR = 0
                self.response.sf.M = 0
                self.response.sf.CRD = 0
                self.response.sf.SCT = 0
                self.response.sf.SC = 0
        except Exception as e:
            pass
        return True

    def verify_response(self, actual_rsp, expected_rsp):
        pass

    def parse_discover_cmd(self, response: bytes, index: int):
        response = response.decode()
        occurences = [m.start() for m in re.finditer('subnqn', response)]
        index = 0 if len(occurences)==1 else index
        start = 7 + occurences[index]
        end = response.find('\n', start)
        nqn = response[start:end].strip()     
        return nqn
        
    def prepare_admin_passthru_cmd(self, command):
        """
        """
        opcode = command.cdw0.OPC
        nsid = command.NSID
        cmd = f"nvme admin-passthru {self.dev_path} --opcode={opcode} -n {nsid}"
        cmd = f"{cmd} --cdw2={command.cdw2.raw} --cdw3={command.cdw3.raw}"
        cmd = f"{cmd} --cdw10={command.cdw10.raw} --cdw11={command.cdw11.raw}"
        cmd = f"{cmd} --cdw12={command.cdw12.raw} --cdw13={command.cdw13.raw}"
        cmd = f"{cmd} --cdw14={command.cdw14.raw} --cdw15={command.cdw15.raw}"

        return cmd


    def submit_discover_cmd(self, transport, address, svcid):
        cmd = "nvme discover"
        cmd = f"{cmd} -t {transport}"
        cmd = f"{cmd} -a {address}"
        cmd = f"{cmd} -s {svcid}"
        cmd = f"{cmd}"
        status = self.execute_cmd(cmd)
        if status==0:
            return 0, self.stdout
        else:
            return 1, self.stderr
    def submit_connect_cmd(self, transport, address, svcid, nqn, kato=None, duplicate=False, hostnqn=None, hostid=None, nr_io_queues=None):
        cmd = "nvme connect"
        cmd = f"{cmd} -t {transport}"
        cmd = f"{cmd} -a {address}"
        cmd = f"{cmd} -s {svcid}"
        cmd = f"{cmd} -n {nqn}"
        if kato!=None:
            cmd = f"{cmd} -k {kato}"
        if hostnqn!=None:
            cmd = f"{cmd} -q {hostnqn}"
        if hostid!=None:
            cmd = f"{cmd} -I {hostid}"
        if nr_io_queues!=None:
            cmd = f"{cmd} -i {nr_io_queues}"
        if duplicate:
            cmd = f"{cmd} -D"
        status = self.execute_cmd(cmd)
        
        alreadyConnected = self.stderr.decode().strip().endswith("Operation already in progress")
        
        if status==0:
            return 0, self.stdout
        else:
            if alreadyConnected:
                return 1, "Already connected to device."
            return 2, self.stderr
    
    def submit_disconnect_cmd(self, nqn=None, device_path=None):
        cmd = "nvme disconnect"
        if nqn:
            cmd = f"{cmd} -n {nqn}"
        elif device_path:
            cmd = f"{cmd} -d {device_path}"
        else:    
            cmd = f"{cmd} -d {self.dev_path}"
        
        status = self.execute_cmd(cmd)
        
        if status==0:
            return 0, self.stdout
        else:
            return 1, self.stderr
        
    def submit_list_subsys_cmd(self):
        cmd = "nvme list-subsys -o json"
        status = self.execute_cmd(cmd)
        if status==0:
            return 0, self.stdout
        else:
            return 1, self.stderr
        
    def submit_list_ns_cmd(self):
        cmd = "nvme list-ns"
        cmd = f"{cmd} {self.dev_path}"
        status = self.execute_cmd(cmd)
        if status==0:
            ns_paths = []
            lines = self.stdout.decode().splitlines()
            for i in range(len(lines)):
                ns_paths.append(self.dev_path+'n'+lines[i][-1])
            return 0, ns_paths
        else:
            return 1, self.stderr
        
    def submit_passthru(self, nvme_cmd, verify_rsp=True, async_run=False):
        command = nvme_cmd.cmd.identify_cmd
        response = nvme_cmd.rsp.response
        data_len = nvme_cmd.buff_size
        if command.cdw0.OPC == 0x06:
            # Admin Command
            cmd = self.prepare_admin_passthru_cmd(command)
            cmd = f"{cmd} --data-len={data_len} -r -b"
        ret_status = self.execute_cmd(cmd)

        if ret_status!=0:
            print("Command execution unsuccessful: ", ret_status)
            return ret_status
        if verify_rsp:
            #self.validate_response()
            #raise Exception("Response invalid")
            pass
        if not response:
            print("Empty response ")
            return ret_status
        
        if len(self.stderr) == 0:
            ctypes.memmove(nvme_cmd.buff, self.stdout, 4096)
            return 0

import json
if __name__ == "__main__":
    status, response = NVMeCLILib("/dev/nvme2").submit_disconnect_cmd()
    if status==0:
        print(response)
    pass