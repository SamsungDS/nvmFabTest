# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

import json
from pytest_metadata.plugin import metadata_key
import loguru
import subprocess
import pytest_html

f = open("config/ts_config.json")
ts_config = json.load(f)
f.close()


def pytest_html_report_title(report):
    """ Setting Title for the HTML report generated"""
    report.title = "Fabric Test Suite: NVMe over Fabric Compliance Test Report (nvmfabtest)"
    report.additional_summary["prefix"] = "BLAH BLAH prefix"
    report.additional_summary["summary"] = "BLAH BLAH summary"
    report.additional_summary["postfix"] = "BLAH BLAH postfix"
    
    report.data["environment"]["Packages"]["loguru"] = str(loguru.__version__)
    report.data["environment"]["Packages"]["pytest_html"] = str(pytest_html.__version__)
    p = subprocess.run("nvme --version", shell=True, capture_output=True)
    p = p.stdout.decode()

    report.data["environment"]["nvme-cli version"]= p[13:p.find("\n")]
    
    del report.data["environment"]["Plugins"]
    del report.data["environment"]["Packages"]["pluggy"]
