import pytest
import sys
sys.path.insert(1, "lib")

from nvme_types import *
from nvme_commands import *
from logging_module import logger
MIN_ASCII_VALUE = 32 
MAX_ASCII_VALUE = 126

class TestIdentifyController:
    status, response, error = NVMeCommands().identify_controller()

    def test_identify_controller_success(self):
        assert self.status==0, self.error

    def test_identify_controller_sn(self):
        b = bytearray(self.response.SN)
        for i in b:
            assert MIN_ASCII_VALUE <= i < MAX_ASCII_VALUE, "ASCII Text in Serial Number not in range"

    def test_identify_controller_mn(self):
        b = bytearray(self.response.MN)
        for i in b:
            assert MIN_ASCII_VALUE <= i < MAX_ASCII_VALUE, "ASCII Text in Serial Number not in range"

    def test_identify_controller_fr(self):
        b = bytearray(self.response.FR)
        for i in b:
            assert MIN_ASCII_VALUE <= i < MAX_ASCII_VALUE, "ASCII Text in Serial Number not in range"

if __name__ == '__main__':
    TestIdentifyController().test_identify_controller_success()