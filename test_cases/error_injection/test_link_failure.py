# Copyright (c) 2024 Samsung Electronics Corporation
# SPDX-License-Identifier: BSD-3-Clause

'''
Simulates a Link down and then a Link up
'''

from src.macros import *
from test_cases.conftest import fabConfig
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
    def setup_method(self, fabConfig, should_run_link_failure):
        ''' Setup Test Case by initialization of objects '''

        self.skipped = False
        if not should_run_link_failure:
            self.skipped = True
            pytest.skip("Link Failure Test disabled")
        logger.info("\n" + "-"*100)
        logger.info("Setup TestCase: Link Failure")
        self.fabConfig = fabConfig
        device = self.fabConfig.device
        self.dev_name = self.fabConfig.device[5:]
        application = self.fabConfig.application
        self.controller = Controller(device, application)

        self.iface = self.controller.sys.get_network_interface()
        logger.info("Network interface: {}", self.iface)
        
        # SETUP - Device Status
        self.output = []
        ret_code, response = self.controller.app.submit_list_subsys_cmd()

        if ret_code == 0:
            j = json.loads(response.decode())
            for i in range(len(j[0]["Subsystems"])):
                subsys = j[0]["Subsystems"][i]
                path = subsys["Paths"][0]
                if path["Name"].strip() == self.dev_name:
                    self.i = i
                    self.output.append(f"-- {self.dev_name} Status: " + path["State"])
                    break
            else:
                logger.log("FAIL", "Didn't find device for setup")
                assert False, "Didn't find device for setup"

    def test_link_failure(self, fabConfig):
        ''' Sending the command and verifying response '''
        try:
            # LINKDOWN
            self.controller.sys.set_link( "down", self.iface)
            self.output.append("Link Down")

            # SLEEP 30secs
            self.output.append("-- Sleeping ZzZ")
            self.controller.sys.sleep(30)
            self.output.append("-- Woke up after 30 seconds")

            # DEVICE STATUS
            ret_code, response = self.controller.app.submit_list_subsys_cmd()

            if ret_code == 0:
                j = json.loads(response.decode())
                j = j[0]["Subsystems"][self.i]["Paths"][0]
                if j["Name"].strip() == self.dev_name:
                    self.output.append(
                        f"-- {self.dev_name} status: " + j["State"])
                else:
                    logger.log("FAIL", "Device lost after link down")
                    assert False, "Device lost after link down"

            # LINKUP
            self.controller.sys.set_link( "up", self.iface)
            self.output.append("Link Up")

        except Exception as e:
            logger.exception(e)
            cmd = f"ip link set {self.iface} up"
            subprocess.Popen(cmd, shell=True)
            raise e

        ret_code, response = self.controller.app.submit_list_subsys_cmd()
        if ret_code == 0:
            j = json.loads(response.decode())
            j = j[0]["Subsystems"][self.i]["Paths"][0]
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
                j = j[0]["Subsystems"][self.i]["Paths"][0]
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

        self.controller.sys.execute_cmd(cmd)

        stdout, stderr = self.controller.sys.stdout, self.controller.sys.stderr
        ret_code = self.controller.sys.ret_code
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
        self.controller.sys.set_link( "up", self.iface)
        self.output.append("Link Up")        
        
        for line in self.output:
            logger.info(line)
        logger.info("-"*100)
