import sys
sys.path.insert(1, "/root/nihal223/nvmfabtest")
import json
import pytest
from lib.cmdlib.commands_lib import NVMeCommandLib
from lib.applib.nvme_cli_lib import NVMeCLILib 
from lib.devlib.device_lib import DeviceConfig
from src.utils.nvme_utils import get_dev_from_subsys


f = open("config/ts_config.json")
ts_config = json.load(f)
f.close()


def connectByIP(app, cmd_lib, connect_details):

    tr = connect_details["transport"]
    addr = connect_details["addr"] 
    svc = connect_details["svcid"]
    # Start Discover Command
    status, response = app.submit_discover_cmd(transport=tr, address=addr, svcid=svc)
    if status!=0:
        print("-- -- Session Setup Error: Discover command failed. Check the configuration details")
        sys.exit(0)
    
    nqn = cmd_lib.parse_discover_cmd(response)
    # End Discover Command

    del response, status
    
    # Start Connect Command
    status = app.submit_connect_cmd(transport=tr, address=addr, svcid=svc, nqn=nqn)
    if status!=0:
        print("-- Session Setup Error: Connect failed. Check the configuration details or connection is already made.")
    # End Connect Command

    #Verify connection and set device path
    status, response = app.submit_list_subsys_cmd()
    if status!=0:
        print("-- Command failed. Check if nvme cli tool is installed")
    
    status, response = get_dev_from_subsys(response, nqn)
    if status!=0:
        print(f"-- Session Setup Error: {response}")
    
    dev_path = response
    return dev_path

#Setup session
@pytest.fixture(scope='session', autouse=True)
def session_setup():
    print("\n\nSetting up session")
    if ts_config["connectByIP"]:
        connect_details = ts_config["connectDetails"]
        
    
        app = NVMeCLILib()
        cmd_lib = NVMeCommandLib(ts_config["device_path"], ts_config["app_name"])

        dev_path = connectByIP(app, cmd_lib, connect_details)
    else:
        dev_path = ts_config["device_path"]
        

    print(dev_path)

    #Complete
    print("Completed Session Setup\n")




@pytest.fixture
def dummy():
    
    dum = DeviceConfig(ts_config["device_path"], ts_config["app_name"])
    return dum

