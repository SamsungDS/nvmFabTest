# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Simulates a Link down and then a Link up
'''

from src.macros import *
from test_cases.conftest import dummy
from lib.structlib.struct_admin_data_lib import IdentifyControllerData
from lib.devlib.device_lib import Controller
from utils.logging_module import logger
import subprocess
import time
import json
import pytest


class TestLinkFailure:
    '''
    Simulates a Link down and then a Link up
    '''

    @pytest.fixture(scope='function', autouse=True)
    def setup_method(self, dummy, should_run_link_failure):
        ''' Setup Test Case by initialization of objects '''

        self.skipped = False
        if not should_run_link_failure:
            self.skipped = True
            pytest.skip("Link Failure Test disabled")
        logger.info("\n", "-"*100)
        logger.info("Setup TestCase: Link Failure")
        self.dummy = dummy
        device = self.dummy.device
        self.dev_name = self.dummy.device[5:]
        application = self.dummy.application
        self.controller = Controller(device, application)

        cmd = "route | grep \'^default\' | grep -o \'[^ ]*$\'"
        p = subprocess.run(cmd, shell=True, capture_output=True)
        self.iface = p.stdout.decode()[:-1]

        # SETUP - Device Status
        self.output = []
        ret_code, response = self.controller.app.submit_list_subsys_cmd()

        if ret_code == 0:
            j = json.loads(response.decode())
            j = j[0]["Subsystems"][0]["Paths"][0]
            if j["Name"].strip() == self.dev_name:
                self.output.append(f"-- {self.dev_name} Status: " + j["State"])
            else:
                logger.log("FAIL", "Didn't find device for setup")
                assert False, "Didn't find device for setup"

    def test_link_failure(self, dummy):
        ''' Sending the command and verifying response '''
        try:
            # LINKDOWN
            cmd = f"ip link set {self.iface} down"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
            p.wait()
            self.output.append("Link Down")

            # SLEEP 30secs
            cmd = "sleep 30"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
            self.output.append("-- Sleeping ZzZ")
            p.wait()
            self.output.append("-- Woke up after 30 seconds")

            # DEVICE STATUS
            ret_code, response = self.controller.app.submit_list_subsys_cmd()

            if ret_code == 0:
                j = json.loads(response.decode())
                j = j[0]["Subsystems"][0]["Paths"][0]
                if j["Name"].strip() == self.dev_name:
                    self.output.append(
                        f"-- {self.dev_name} status: " + j["State"])
                else:
                    logger.log("FAIL", "Device lost after link down")
                    assert False, "Device lost after link down"

            # LINKUP
            cmd = f"ip link set {self.iface} up"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
            p.wait()
            self.output.append("Link Up")

        except Exception as e:
            logger.exception(e)
            cmd = f"ip link set {self.iface} up"
            subprocess.Popen(cmd, shell=True)
            raise e

        ret_code, response = self.controller.app.submit_list_subsys_cmd()
        if ret_code == 0:
            j = json.loads(response.decode())
            j = j[0]["Subsystems"][0]["Paths"][0]
            isLive = j["State"].strip(
            ) == "live" and j["Name"].strip() == self.dev_name
            self.output.append(f"-- {self.dev_name} status: " + (
                j["State"] if j["Name"].strip() == self.dev_name else "not connected"))

        self.output.append("Waiting . .. ...")

        start = time.time()
        while not isLive:
            ret_code, response = self.controller.app.submit_list_subsys_cmd()
            if ret_code == 0:
                j = json.loads(response.decode())
                j = j[0]["Subsystems"][0]["Paths"][0]
                isLive = j["State"].strip(
                ) == "live" and j["Name"].strip() == self.dev_name

            if time.time() - start > 60:
                logger.log("FAIL", "Device failed to come back up")
                assert False, "Device failed to come back up"

        end = time.time()

        self.output.append("-- waited " + str(end-start) +
                           " seconds since linkup")
        self.output.append(f"-- {self.dev_name} status: live")
        cmd = "fio"
        dev = "/dev/"+self.dev_name+"n1"
        cmd = f"{cmd} --filename={dev}"
        cmd = f"{cmd} --ioengine=libaio"
        cmd = f"{cmd} --rw=write"
        cmd = f"{cmd} --runtime=59999ms"
        cmd = f"{cmd} --group_reporting"
        cmd = f"{cmd} --name=LinkUpDown_Test"
        cmd = f"{cmd} --do_verify=1"
        cmd = f"{cmd} --verify=crc32"

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret_code = p.returncode
        if ret_code == 0 and "verify" not in stdout.decode():
            self.output.append("fio success with data integrity")
        elif ret_code != 0 and "verify" not in stderr.decode():
            logger.log("FAIL", f"fio testing failed\n{ret_code, stderr.decode()}")
            assert False, f"fio testing failed\n{ret_code, stderr.decode()}"
        else:
            logger.log("FAIL", f"Data integrity verification failed during fio testing\n{
                         ret_code, stderr.decode()}"
                         )
            assert False, f"Data integrity verification failed during fio testing\n{
                ret_code, stderr.decode()}"

    def teardown_method(self):
        ''' Teardown of Test Case '''
        if self.skipped:
            return
        logger.info("Teardown TestCase: Link Failure")
        cmd = f"ip link set {self.iface} up"
        subprocess.Popen(cmd, shell=True)
        for line in self.output:
            logger.info(line)
        logger.info("-"*100)
