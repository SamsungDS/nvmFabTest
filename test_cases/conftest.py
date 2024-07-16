# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

"""
Configurations for pytest and test utilities.
This file contains test fixtures and helper functions for setting up
and tearing down a session for NVMe over Fabric compliance testing.
"""

import json
import pytest
import sys
sys.path.insert(1, "./")
from lib.cmdlib.commands_lib import NVMeCommandLib
from lib.applib.nvme_cli_lib import NVMeCLILib
from lib.devlib.device_lib import *
from utils.logging_module import logger
from src.utils.nvme_utils import parse_for_already_connected
from utils.reporting_module import *


f = open("config/ts_config.json")
ts_config = json.load(f)
f.close()


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
        logger.error("-- -- Session Setup Error: Discover command failed. Check the configuration details")
        return status, response
    nqn = app.get_nqn_from_discover(response, index)
    # End Discover Command

    # Check Device already connected
    status, response = app.submit_list_subsys_cmd()
    if status != 0:
        logger.error("-- -- Command failed. Check if nvme cli tool is installed")
        return status, response
    status, alreadyConnected, response = parse_for_already_connected(
        response, connect_details, nqn)
    logger.info("-- Already connected: {}", alreadyConnected)
    if status != 0:
        logger.error(f"-- -- Session Setup Error: {status, response}")
        return status, response

    if not alreadyConnected:
        logger.info("-- -- Device not connected, attempting connection.")
        # Start Connect Command
        status, response = app.submit_connect_cmd(
            transport=tr, address=addr, svcid=svc, nqn=nqn)  # , dhchap_host=dhchap)
        if status != 0:
            logger.error(
                "-- -- Session Setup Error: Connect failed. Check the configuration details")
            return status, response

    logger.info("-- Device connected. Fetching device_path.")
    dev_path = response
    return 0, dev_path


@pytest.fixture(scope='session', autouse=True)
def session_setup():
    """ Session setup for Test Suite """

    logger.info("\n")
    logger.info("-"*30 + " Setting up session " + "-"*50)

    if ts_config["connectByIP"].lower() == "true":
        connect_details = ts_config["connectDetails"]
        app = NVMeCLILib()
        cmd_lib = NVMeCommandLib(ts_config["app_name"])

        status, response = connectByIP(app, cmd_lib, connect_details)
        if status == 0:
            dev_path = response
        else:
            if ts_config["device_path"][:-1] == "/dev/nvme" or ts_config["device_path"][:-3] == "/dev/nvme":
                logger.warning("-- ErrorConnecting, using device_path instead: ", response)
                dev_path = ts_config["device_path"]
            else:
                logger.error("-- Error Connecting and no device_path specified: ", response)
                assert False
    else:
        dev_path = ts_config["device_path"]

    logger.info("-"*30 + "Completed session setup "+ "-"*50 + "\n")
    logger.success("Path being used for testcases: {}\n", dev_path)

    yield dev_path

    logger.info("\n")
    logger.info("Session Teardown:")
    if ts_config["disconnectOnDone"].lower() == "true":
        status, res = app.submit_disconnect_cmd(device_path=dev_path)
        if status != 0:
            logger.error(f"Disconnect failed: {res}")
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
