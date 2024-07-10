"""
Configurations for pytest and test utilities.
This file contains test fixtures and helper functions for setting up
and tearing down a session for NVMe over Fabric compliance testing.
"""

import json
import pytest
import sys
sys.path.insert(1, "./../nvmeof_compliance")
from lib.cmdlib.commands_lib import NVMeCommandLib
from lib.applib.nvme_cli_lib import NVMeCLILib
from lib.devlib.device_lib import *
from src.utils.nvme_utils import *
from lib.applib.libnvme_lib import Libnvme


f = open("config/ts_config.json")
ts_config = json.load(f)
f.close()


def pytest_html_report_title(report):
    """ Setting Title for the HTML report generated"""
    report.title = "NVMe over Fabric Compliance Test Report (nvmfabtest)"


def connectByIP(app: NVMeCLILib, cmd_lib: NVMeCommandLib, connect_details):
    """
    Connects to a NVM device using the details given in the arguments.

    Args:
        app (NVMeCLILib): An instance of the NVMeCLILib class.
        cmd_lib (NVMeCommandLib): An instance of the NVMeCommandLib class.
        connect_details (dict): A dictionary containing the connection details,
            including the transport, address, svcid, and index.

    Returns:
        Tuple[int, str]: A tuple containing the status and the error/device path.
    """

    tr = connect_details["transport"]
    addr = connect_details["addr"]
    svc = connect_details["svcid"]
    index = connect_details["index"]

    # Start Discover Command
    status, response = app.submit_discover_cmd(
        transport=tr, address=addr, svcid=svc)
    if status != 0:
        print("-- -- Session Setup Error: Discover command failed. Check the configuration details")
        return status, response
    nqn = app.get_nqn_from_discover(response, index)
    # End Discover Command

    # Check Device already connected
    status, response = app.submit_list_subsys_cmd()
    if status != 0:
        print("-- -- Command failed. Check if nvme cli tool is installed")
        return status, response
    status, alreadyConnected, response = parse_for_already_connected(
        response, connect_details, nqn)
    print("-- Already connected: ", alreadyConnected)
    if status != 0:
        print(f"-- -- Session Setup Error: {status, response}")
        return status, response

    if not alreadyConnected:
        print("-- -- Device not connected, attempting connection.")
        # Start Connect Command
        status, response = app.submit_connect_cmd(
            transport=tr, address=addr, svcid=svc, nqn=nqn)  # , dhchap_host=dhchap)
        if status != 0:
            print(
                "-- -- Session Setup Error: Connect failed. Check the configuration details")
            return status, response

    print("-- Device connected. Fetching device_path.")
    dev_path = response
    return 0, dev_path


@pytest.fixture(scope='session', autouse=True)
def session_setup():
    """ Session setup for Test Suite """

    print("\n")
    print("-"*30, " Setting up session ", "-"*50)

    if ts_config["connectByIP"].lower() == "true":
        connect_details = ts_config["connectDetails"]
        app = NVMeCLILib()
        cmd_lib = NVMeCommandLib(ts_config["app_name"])

        status, response = connectByIP(app, cmd_lib, connect_details)
        if status == 0:
            dev_path = response
        else:
            if ts_config["device_path"][:-1] == "/dev/nvme" or ts_config["device_path"][:-3] == "/dev/nvme":
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
    if ts_config["disconnectOnDone"].lower() == "true":
        status, res = app.submit_disconnect_cmd(device_path=dev_path)
        if status != 0:
            raise Exception(f"Disconnect failed: {res}")


@pytest.fixture
def dummy(session_setup):
    """ Fixture for providing Device Config details """
    dev_path = session_setup
    dum = DeviceConfig(dev_path, ts_config["app_name"])
    return dum


@pytest.fixture
def connectDetails():
    """ Fixture for providing Connection Details """
    data = ts_config["connectDetails"]
    connect_details = ConnectDetails()
    connect_details.transport = data["transport"]
    connect_details.address = data["addr"]
    connect_details.svcid = data["svcid"]
    connect_details.index = data["index"]

    return connect_details


@pytest.fixture
def authDetails():
    """ Fixture for providing Connection Details """

    data = ts_config["test_auth_config"]
    auth_details = AuthDetails()
    auth_details.should_test = ts_config["test_authentication"]
    auth_details.transport = data["transport"]
    auth_details.address = data["addr"]
    auth_details.svcid = data["svcid"]
    auth_details.index = data["index"]
    auth_details.dhchap_host = data["dhchap_host"]
    auth_details.hostnqn = data["hostnqn"]

    return auth_details


@pytest.fixture
def should_run_link_failure():
    """ Fixture for providing Connection Details """

    data = ts_config["test_link_failure"]
    if data.lower() == "true":
        return True
    else:
        return False
