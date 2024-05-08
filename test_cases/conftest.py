import sys, os
sys.path.insert(1, "/root/nihal223/nvmfabtest")
import json
import pytest
from lib.cmdlib.commands_lib import NVMeCommandLib
from lib.applib.nvme_cli_lib import NVMeCLILib
from lib.applib.libnvme_wrap import Libnvme 
from lib.devlib.device_lib import ConnectDetails, DeviceConfig
from src.utils.nvme_utils import *

f = open("config/ts_config.json")
ts_config = json.load(f)
f.close()

def pytest_html_report_title(report):
   report.title = "NVMe over Fabric Compliance Test Report (nvmfabtest)"
   
def connectByIP(app: NVMeCLILib, cmd_lib: NVMeCommandLib, connect_details):

    tr = connect_details["transport"]
    addr = connect_details["addr"] 
    svc = connect_details["svcid"]
    index = connect_details["index"]

    # Start Discover Command
    status, response = app.submit_discover_cmd(transport=tr, address=addr, svcid=svc)
    if status!=0:
        print("-- -- Session Setup Error: Discover command failed. Check the configuration details")
        return status, response
    nqn = app.parse_discover_cmd(response, index)
    # End Discover Command
    
    #Check Device already connected
    status, response = app.submit_list_subsys_cmd()
    if status!=0:
        print("-- -- Command failed. Check if nvme cli tool is installed")
        return status, response
    
    status, alreadyConnected, response = parse_for_already_connected(response, connect_details, nqn)
    if status!=0:
        print(f"-- -- Session Setup Error: {response}")
        return status, response

    if not alreadyConnected:
        print("-- -- Device not connected, attempting connection.")
        # Start Connect Command
        status, response = app.submit_connect_cmd(transport=tr, address=addr, svcid=svc, nqn=nqn)
        if status!=0:
            print("-- -- Session Setup Error: Connect failed. Check the configuration details")
            return status, response
        # if status==1:
        #     print("-- -- Device already connected. Fetching device_path.")

        #Verify connection and set device path
        status, response = app.submit_list_subsys_cmd()
        if status!=0:
            print("-- -- Command failed. Check if nvme cli tool is installed")
            return status, response
        
        status, response = get_dev_from_subsys(response, nqn)
        if status!=0:
            print(f"-- -- Session Setup Error: {response}")
            return status, response
    print("-- Device connected. Fetching device_path.")     
    dev_path = response
    return 0, dev_path


#Setup session
@pytest.fixture(scope='session', autouse=True)
def session_setup():
    print("\n")
    print("-"*30, " Setting up session ", "-"*50)
    
    if ts_config["connectByIP"].lower()=="true":
        connect_details = ts_config["connectDetails"]
        app = NVMeCLILib()
        cmd_lib = NVMeCommandLib(ts_config["app_name"])

        status, response = connectByIP(app, cmd_lib, connect_details)
        if status==0:
            dev_path = response
        else:
            if ts_config["device_path"][:-1]=="/dev/nvme" or ts_config["device_path"][:-3]=="/dev/nvme":
                print("-- ErrorConnecting, using device_path instead: ", response)
                dev_path = ts_config["device_path"]
            else:
                print("-- Error Connecting and no device_path specified: ", response)
                assert False
    else:
        dev_path = ts_config["device_path"]
    
    print("-"*30, "Completed session setup ", "-"*50, "\n")
    print("Path being used for testcases: ", dev_path, "\n")
    
    yield dev_path

    print("\nSession Teardown:")
    if ts_config["disconnectOnDone"].lower()=="true":
        status, res = app.submit_disconnect_cmd(device_path=dev_path)
        if status!=0:
            raise Exception(f"Disconnect failed: {res}")

@pytest.fixture
def dummy(session_setup):

    dev_path = session_setup
    dum = DeviceConfig(dev_path, ts_config["app_name"])
    # dum = DeviceConfig(dev_path, ts_config["app_name"])
    return dum

@pytest.fixture
def connectDetails():
    data = ts_config["connectDetails"]
    connect_details = ConnectDetails()
    connect_details.transport = data["transport"]
    connect_details.address = data["addr"] 
    connect_details.svcid = data["svcid"]
    connect_details.index = data["index"]
    
    return connect_details