""" 
libnvme interface library.

Library that provides an interface for interacting with NVMe devices
using libnvme.
This library is designed to be used in the framework that requires
interaction with NVMe devices, and it abstracts the complexities
of dealing with the libnvme APIs and it's source code.
"""
import sys
sys.path.insert(1, "./../nvmeof_compliance/")
from lib.cmdlib.commands_lib import NVMeCommandLib
from lib.structlib.struct_base_lib import GenericCommand
from lib.structlib.nvme_struct_main_lib import NVMeCommand, NVMeRspStruct
from utils.logging_module import logger
import ctypes
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.structlib.struct_fabric_libnvme_lib import *
import os
import re
import json


class Libnvme():

    def __init__(self, dev_path=None) -> None:
        """ - Initialize attributes for the CLI Library
            - Sets the path for the shared object file.
            - Defines the function prototypes of the libnvme C methods.
        Args:
            dev_path (str, optional): Device path to which commands need to be sent.
                Defaults to None.
        """
        if re.match(r"\A/dev/nvme[0-9]+(n[0-9]+)?\Z", dev_path):
            self.dev_name = dev_path[5:]
            print("-- Default configured device for libnvme: ", self.dev_name)
        elif re.match(r"\Anvme[0-9]+(n[0-9]+)?\Z", dev_path):
            self.dev_name = dev_path
            print("-- Default configured device for libnvme: ", self.dev_name)
        elif not dev_path:
            pass
        else:
            print("--",
                dev_path, " not in format of /dev/nvmeX or /dev/nvmeXnY or nvmeX or nvmeXnY")
            raise NameError(
                dev_path, " not in format of /dev/nvmeX or /dev/nvmeXnY or nvmeX or nvmeXnY")

        self.connectedDeviceName = None
        self.command = None
        self.response = None
        self.cmdlib = NVMeCommandLib("libnvme")
        libnvme_path = Libnvme.get_libnvme_path()
        print(f"-- libnvme initializing, using path {libnvme_path}")
        self.libnvme = ctypes.CDLL(libnvme_path)

        # void nvmf_default_config(struct nvme_fabrics_config *cfg);
        self.libnvme.nvmf_default_config.argtypes = [
            ctypes.POINTER(NVME_FABRICS_CONFIG)]
        self.libnvme.nvmf_default_config.restype = None

        # nvme_root_t nvme_scan(const char *config_file);
        self.libnvme.nvme_scan.argtypes = [ctypes.c_char_p]
        self.libnvme.nvme_scan.restype = ctypes.POINTER(NVME_ROOT)

        # nvme_host_t nvme_default_host(nvme_root_t r);
        self.libnvme.nvme_default_host.argtypes = [ctypes.POINTER(NVME_ROOT)]
        self.libnvme.nvme_default_host.restype = ctypes.POINTER(NVME_HOST)

        # nvme_ctrl_t nvme_create_ctrl(nvme_root_t r,
        #         const char *subsysnqn, const char *transport,
        #         const char *traddr, const char *host_traddr,
        #         const char *host_iface, const char *trsvcid);
        self.libnvme.nvme_create_ctrl.argtypes = [
            ctypes.POINTER(NVME_ROOT)]+[ctypes.c_char_p]*6
        self.libnvme.nvme_create_ctrl.restype = ctypes.POINTER(NVME_CTRL)

        # int nvmf_add_ctrl(nvme_host_t h, nvme_ctrl_t c,
        #       const struct nvme_fabrics_config *cfg);
        self.libnvme.nvmf_add_ctrl.argtypes = [ctypes.POINTER(
            NVME_HOST), ctypes.POINTER(NVME_CTRL), ctypes.POINTER(NVME_FABRICS_CONFIG)]
        self.libnvme.nvmf_add_ctrl.restype = ctypes.c_int

        # int nvmf_get_discovery_log(nvme_ctrl_t c, struct nvmf_discovery_log **logp,
        #         int max_retries);
        self.libnvme.nvmf_get_discovery_log.argtypes = [ctypes.POINTER(
            NVME_CTRL), ctypes.POINTER(ctypes.POINTER(NVMF_DISCOVERY_LOG)), ctypes.c_int]
        self.libnvme.nvmf_get_discovery_log.restype = ctypes.c_int

        # int nvme_disconnect_ctrl(nvme_ctrl_t c);
        self.libnvme.nvme_disconnect_ctrl.argtypes = [
            ctypes.POINTER(NVME_CTRL)]
        self.libnvme.nvme_disconnect_ctrl.restype = ctypes.c_int

        # void nvme_free_ctrl(struct nvme_ctrl *c);
        self.libnvme.nvme_free_ctrl.argtypes = [ctypes.POINTER(NVME_CTRL)]
        self.libnvme.nvme_free_ctrl.restype = None

        # void nvme_free_tree(nvme_root_t r);
        self.libnvme.nvme_free_tree.argtypes = [ctypes.POINTER(NVME_ROOT)]
        self.libnvme.nvme_free_tree.restype = None

        # nvme_ctrl_t nvme_ctrl_find(nvme_subsystem_t s, const char *transport,
        # const char *traddr, const char *trsvcid,
        # const char *subsysnqn, const char *host_traddr,
        # const char *host_iface);
        self.libnvme.nvme_ctrl_find.argtypes = [
            ctypes.POINTER(NVME_SUBSYSTEM)]+[ctypes.c_char_p]*6
        self.libnvme.nvme_ctrl_find.restype = ctypes.POINTER(NVME_CTRL)

        # nvme_subsystem_t nvme_lookup_subsystem(struct nvme_host *h,
        # const char *name,
        # const char *subsysnqn);
        self.libnvme.nvme_lookup_subsystem.argtypes = [
            ctypes.POINTER(NVME_HOST)]+[ctypes.c_char_p]*2
        self.libnvme.nvme_lookup_subsystem.restype = ctypes.POINTER(
            NVME_SUBSYSTEM)

        # nvme_ctrl_t nvme_lookup_ctrl(nvme_subsystem_t s, const char *transport,
        # const char *traddr, const char *host_traddr,
        # const char *host_iface, const char *trsvcid,
        # nvme_ctrl_t p);
        self.libnvme.nvme_lookup_ctrl.argtypes = [ctypes.POINTER(
            NVME_SUBSYSTEM)] + [ctypes.c_char_p]*5 + [ctypes.POINTER(NVME_CTRL)]
        self.libnvme.nvme_lookup_ctrl.restype = ctypes.POINTER(NVME_CTRL)

        # nvme_host_t nvme_first_host(nvme_root_t r);
        self.libnvme.nvme_first_host.argtypes = [ctypes.POINTER(NVME_ROOT)]
        self.libnvme.nvme_first_host.restype = ctypes.POINTER(NVME_HOST)

        # nvme_host_t nvme_next_host(nvme_root_t r, nvme_host_t h);
        self.libnvme.nvme_next_host.argtypes = [
            ctypes.POINTER(NVME_ROOT), ctypes.POINTER(NVME_HOST)]
        self.libnvme.nvme_next_host.restype = ctypes.POINTER(NVME_HOST)

        # nvme_subsystem_t nvme_first_subsystem(nvme_host_t h);
        self.libnvme.nvme_first_subsystem.argtypes = [
            ctypes.POINTER(NVME_HOST)]
        self.libnvme.nvme_first_subsystem.restype = ctypes.POINTER(
            NVME_SUBSYSTEM)

        # nvme_subsystem_t nvme_next_subsystem(nvme_host_t h, nvme_subsystem_t s);
        self.libnvme.nvme_next_subsystem.argtypes = [
            ctypes.POINTER(NVME_HOST), ctypes.POINTER(NVME_SUBSYSTEM)]
        self.libnvme.nvme_next_subsystem.restype = ctypes.POINTER(
            NVME_SUBSYSTEM)

        # nvme_ctrl_t nvme_subsystem_first_ctrl(nvme_subsystem_t s);
        self.libnvme.nvme_subsystem_first_ctrl.argtypes = [
            ctypes.POINTER(NVME_SUBSYSTEM)]
        self.libnvme.nvme_subsystem_first_ctrl.restype = ctypes.POINTER(
            NVME_CTRL)

        # nvme_ctrl_t nvme_subsystem_next_ctrl(nvme_subsystem_t s, nvme_ctrl_t c);
        self.libnvme.nvme_subsystem_next_ctrl.argtypes = [
            ctypes.POINTER(NVME_SUBSYSTEM), ctypes.POINTER(NVME_CTRL)]
        self.libnvme.nvme_subsystem_next_ctrl.restype = ctypes.POINTER(
            NVME_CTRL)

        # const char *nvme_ctrl_get_name(nvme_ctrl_t c);
        self.libnvme.nvme_ctrl_get_name.argtypes = [ctypes.POINTER(NVME_CTRL)]
        self.libnvme.nvme_ctrl_get_name.restype = ctypes.c_char_p

        # void nvme_host_set_dhchap_key(nvme_host_t h, const char *key);
        self.libnvme.nvme_host_set_dhchap_key.argtypes = [ctypes.POINTER(NVME_HOST), ctypes.c_char_p]
        self.libnvme.nvme_host_set_dhchap_key.restype = None    

        # const char *nvme_ctrl_get_subsysnqn(nvme_ctrl_t c); 
        self.libnvme.nvme_ctrl_get_subsysnqn.argtypes = [ctypes.POINTER(NVME_CTRL)]
        self.libnvme.nvme_ctrl_get_subsysnqn.restype = ctypes.c_char_p

        # void nvme_ctrl_set_dhchap_key(nvme_ctrl_t c, const char *key);
        self.libnvme.nvme_host_set_dhchap_key.argtypes = [ctypes.POINTER(NVME_CTRL), ctypes.c_char_p]
        self.libnvme.nvme_host_set_dhchap_key.restype = None 

    @staticmethod
    def get_libnvme_path():
        """Static method used to set the path of the libnvme.so file
            and fine it if needed.

        Raises:
            FileNotFoundError: If unable to find the libnvme.so file anywhere.

        Returns:
            str: Path to the correct libnvme.so file.
        """
        f = open("config/ts_config.json")
        ts_config = json.load(f)
        f.close()

        # Finding system's libnvme.so file
        if ts_config["libnvme_path"].lower() == "auto":
            for root, dirs, files in os.walk("/usr/"):
                if "libnvme.so" in files:
                    return os.path.join(root, "libnvme.so")

            for root, dirs, files in os.walk("/"):
                if "libnvme.so" in files:
                    return os.path.join(root, "libnvme.so")

            print("--",
                "Not able to find libnvme.so. Give the path manually in ts_config.json.")
            raise FileNotFoundError(
                "Not able to find libnvme.so. Give the path manually in ts_config.json.")

        elif ts_config["libnvme_path"].endswith("libnvme.so") and os.path.isfile(ts_config["libnvme_path"]):
            return ts_config["libnvme_path"]
        else:
            print("-- libnvme.so path not correct. Set to \"auto\" to find automatically.")
            raise FileNotFoundError(
                "libnvme.so path not correct. Set to \"auto\" to find automatically.")
    
    def nvme_open(self):
        """Wrapper for the nvme_open method in libnvme. 

        Returns:
            Tuple[int, str]: Tuple containing status and error message (empty if success)
        """
        device_name = self.dev_name
        nvme_open = self.libnvme.nvme_open
        nvme_open.argtypes = [ctypes.c_char_p]
        nvme_open.restype = ctypes.c_int
        device_descriptor = nvme_open(device_name.encode())
        if device_descriptor < 0:
            return device_descriptor, f"Failed to open NVMe device {device_name}. Error code {device_descriptor}"
        else:
            self.device_descriptor = device_descriptor
            return 0, ""

    def submit_list_ns_cmd(self):
        """Sends identify command with CNS=02 to retrieve active namespace list

        Returns:
            Tuple[int, List[str] | str]:
            - If execution successful, tuple contains status code and list of
                absolute namespace paths.
            - If execution fails, tuple contains status code and stderr.

        """
        nvme_cmd = self.cmdlib.get_identify_cmd()
        result = ctypes.create_string_buffer(4096)

        nvme_cmd.buff = ctypes.addressof(result)
        command = nvme_cmd.cmd.generic_command
        nvme_cmd.cmd.generic_command.dptr.sgl.data_len = 4096
        nvme_cmd.cmd.generic_command.dptr.sgl.addr = nvme_cmd.buff
        nvme_cmd.cmd.identify_cmd.cdw10.raw = 0x02

        status, error = self.nvme_open()
        if status != 0:
            return status, error

        libnvme_submit_admin_passthru = self.libnvme.nvme_submit_admin_passthru
        libnvme_submit_admin_passthru.argtypes = [
            ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
        libnvme_submit_admin_passthru.restype = ctypes.c_int32
        print("-- Structure passed to libnvme is at address ",
              hex(command.dptr.sgl.addr))

        status = libnvme_submit_admin_passthru(
            self.device_descriptor, ctypes.addressof(command), None)
        if status == 0:
            ns_paths = []
            dev = self.dev_name if self.dev_name[-2] != 'n' else self.dev_name[:-2]
            for i in range(0, 4096, 4):
                this_byte = result.raw[i]
                if this_byte == 0:
                    break
                ns_paths.append(dev+'n'+str(this_byte))
            return 0, ns_paths
        else:
            return 1, "ERROR"

    def submit_passthru(self, nvme_cmd, verify_rsp=False, async_run=False):
        """
        Submit a passthru command to the NVMe device.

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
        print("--",
            f"libnvme submit passthru: OPC:{command.cdw0.OPC} NSID:{command.NSID} CDW10:{command.cdw10.raw} CDW11:{command.cdw11.raw}")
        self.ret_status, error = self.nvme_open()
        if self.ret_status != 0:
            print("-- --", error)
            return self.ret_status

        if 0 <= command.cdw0.OPC <= 0x0D:
            # Admin Command
            nvme_cmd.cmd.generic_command.dptr.sgl.data_len = nvme_cmd.buff_size
            nvme_cmd.cmd.generic_command.dptr.sgl.addr = nvme_cmd.buff

            # Prototype definitions
            libnvme_submit_admin_passthru = self.libnvme.nvme_submit_admin_passthru
            libnvme_submit_admin_passthru.argtypes = [
                ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
            libnvme_submit_admin_passthru.restype = ctypes.c_int32

            self.ret_status = libnvme_submit_admin_passthru(
                self.device_descriptor, ctypes.addressof(command), None)
            if self.ret_status != 0:
                print("-- -- Command execution unsuccessful: ", hex(self.ret_status))

        if command.cdw0.OPC == 0x7f:
            # Fabric Command

            # Prototype definitions
            libnvme_submit_admin_passthru = self.libnvme.nvme_submit_admin_passthru64
            libnvme_submit_admin_passthru.argtypes = [
                ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
            libnvme_submit_admin_passthru.restype = ctypes.c_int32

            self.ret_status = libnvme_submit_admin_passthru(
                self.device_descriptor, ctypes.addressof(command), nvme_cmd.buff)
            if self.ret_status != 0:
                print("-- -- Command execution unsuccessful: ", hex(self.ret_status))

        return self.ret_status

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
            Tuple[int, str]: A tuple containing the status code and the stdout or stderr.
        """
        cfg = NVME_FABRICS_CONFIG()
        self.libnvme.nvmf_default_config(ctypes.byref(cfg))

        r = self.libnvme.nvme_scan(None)
        
        h = self.libnvme.nvme_default_host(r)

        if not h:
            return 1, "Failed to allocate memory to host"

        c = self.libnvme.nvme_create_ctrl(r, nqn.encode(),
        transport.encode(), address.encode(), cfg.host_traddr, cfg.host_iface, svcid.encode())

        if not c:
            return 2, "Failed to allocate memory to ctrl"

        # bys = bytes(cfg)
        # count=0
        # for b in bys:
        #     print(count,":",format(b, '08b'))
        #     count=count+1

        if kato:
            cfg.keep_alive_tmo = kato
        if duplicate:
            cfg.duplicate_connect = duplicate
        if nr_io_queues:
            cfg.nr_io_queues = nr_io_queues
        if dhchap_host:
            self.libnvme.nvme_host_set_dhchap_key(h, dhchap_host.encode())
        if dhchap_ctrl:
            self.libnvme.nvme_ctrl_set_dhchap_key(c, dhchap_ctrl.encode())
        
        self.ret_status = self.libnvme.nvmf_add_ctrl(h, c, ctypes.byref(cfg))

        if self.ret_status < 0:
            return self.ret_status, "No controller found"
        
        got_name = str(self.libnvme.nvme_ctrl_get_name(c))[2:-1]
        self.connectedDeviceName = got_name
        print(f"-- Successfully connected to {transport} {address} {svcid} {nqn}")
        print("-- -- Device Name (self.connectedDeviceName):", got_name)

        return 0, "/dev/" + got_name

    def submit_disconnect_cmd(self, nqn=None, dev_name=None):
        """
        Submits a disconnect command to the NVMe fabric device.
        If no arguments are given, then it will disconnect the dev_name attribute
            stored in the object. 
        If dev_name is not set, then raise error.

        Args:
            (TBD) nqn (str, optional): The NQN of the device to disconnect.
            device_path (str, optional): The path of the device to disconnect.  

        Returns:
            Tuple[int, str]: A tuple containing the status code and the error (empty if success)

        Raises:
            NameError: If device path is not in correct format.
        """
        if not dev_name and not nqn:
            dev_name = self.dev_name
        if dev_name:
            if re.match(r"\A/dev/nvme[0-9]+\Z", dev_name):
                dev_name = dev_name[5:]

            if re.match(r"\A/dev/nvme[0-9]+n[0-9]+\Z", dev_name):
                dev_name = dev_name[5:-2]

        if (not dev_name or len(dev_name) == 0) and not nqn:
            raise NameError(
                f"Cannot disconnect this device: {dev_name}")

        print(f"-- Disconnecting {dev_name if dev_name else (nqn if nqn else None)} . . .")
        ctrl = []
    
        r = self.libnvme.nvme_scan(None)
        h = self.libnvme.nvme_first_host(r)
        while h:
            s = self.libnvme.nvme_first_subsystem(h)
            while s:
                c = self.libnvme.nvme_subsystem_first_ctrl(s)
                while c:
                    got_name = str(self.libnvme.nvme_ctrl_get_name(c))[2:-1]
                    if got_name == dev_name:
                        ctrl.append(c)
                        break

                    got_nqn = str(self.libnvme.nvme_ctrl_get_subsysnqn(c))[2:-1]
                    if got_nqn == nqn:
                        ctrl.append(c)
                        # break
                    c = self.libnvme.nvme_subsystem_next_ctrl(s, c)
                else:
                    s = self.libnvme.nvme_next_subsystem(h, s)
                    continue
                break
            else:
                h = self.libnvme.nvme_next_host(r, h)
                continue
            break

        if len(ctrl)==0:
            print("-- -- Device not found")
            return 1, "Disconnect failed, device not found"
        i=0
        for c in ctrl:
            self.ret_status = self.libnvme.nvme_disconnect_ctrl(c)
            i+=1
        print((f"-- Disconnected {i} controller"+("" if i==1 else "s")) if self.ret_status==0 else "Failed Disconnect")
        return self.ret_status, "Disconnect failed" if self.ret_status != 0 else ""


    def get_response(self, nvme_cmd):
        """Fill the CQE structure (TBD)

        Args:
            nvme_cmd: Command object to fill response in

        Returns:
            bool: Indicates success or failure
        """
        response = nvme_cmd.rsp.response
        response.sf.SC = self.ret_status
        response.DNR = 0
        response.sf.M = 0
        response.sf.CRD = 0
        response.sf.SCT = 0
        response.sf.SC = 0
        
if __name__ == '__main__':
    lib = Libnvme("nvme2")
    nqn = NVME_DISCOVERY_NQN
    # nqn = "nqn.2023-01.com.samsung.semiconductor:665e905a-bfde-11d3-01aa-a8a159fba2e6_0_0"
    print("tcp", "10.0.0.220", "4420", nqn)
    print(lib.submit_connect_cmd("tcp", "10.0.0.220", "4420", nqn))
    # lib.submit_connect_cmd("tcp", "10.0.0.220", "4420", nqn, duplicate=True)

    # lib.submit_connect_cmd("tcp", "10.0.0.220", "4420", nqn, nr_io_queues=31)

    # lib.submit_disconnect_cmd(dev_name="/dev/nvme2")
    # lib.submit_disconnect_cmd(nqn)