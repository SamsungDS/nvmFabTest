# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-2-Clause

import json
from pytest_metadata.plugin import metadata_key
import loguru
import pytest_html

from lib.applib.nvme_cli_lib import NVMeCLILib
from lib.devlib.device_lib import Controller

def pytest_html_report_title(report):
    """ Setting Title for the HTML report generated"""
    f = open("config/ts_config.json")
    ts_config = json.load(f)
    f.close()
    
    report.title = "Fabric Test Suite: NVMe over Fabric Compliance Test Report (nvmFabTest)"
    
    report.data["environment"]["Packages"]["loguru"] = str(loguru.__version__)
    report.data["environment"]["Packages"]["pytest_html"] = str(pytest_html.__version__)
    
    cli = NVMeCLILib()
    report.data["environment"]["NVMe Details"] = {}
    report.data["environment"]["NVMe Details"]["driver version"] = cli.get_driver_version()
    report.data["environment"]["NVMe Details"]["nvme-cli version"] = cli.get_app_version()
    report.data["environment"]["NVMe Details"]["nvme-cli path"] = cli.get_app_path()
    
    if len(ts_config["device_path"])!=0:
        if ts_config["device_path"].startswith("/dev/") or ts_config["device_path"].startswith("nvme"):
            report.data["environment"]["Device Path"] = ts_config["device_path"]
    
    if ts_config["connectByIP"].lower() == "true":
        report.data["environment"]["Target Device Details"] = ts_config["connectDetails"]

    report.data["environment"]["Application Selected"] = ts_config["app_name"]

    if ts_config["test_authentication"].lower() == "true":
        del ts_config["test_auth_config"]["dhchap_host"]
        del ts_config["test_auth_config"]["dhchap_ctrl"]
        report.data["environment"]["Authentication Device Details"] = ts_config["test_auth_config"]
    else:
        report.data["environment"]["Authentication Test(s)"] = "Skipped"

    if ts_config["test_link_failure"].lower() == "true":
        report.data["environment"]["Link Failure Test(s)"] = "Executed"
    else:
        report.data["environment"]["Link Failure Test(s)"] = "Skipped"

    del report.data["environment"]["Plugins"]
    del report.data["environment"]["Packages"]["pluggy"]
