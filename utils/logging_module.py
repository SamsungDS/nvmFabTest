"""
Module for creating a logger object which
can be used Test Suite wide for logging.
"""
import logging
from pathlib import Path


dir_path = "./logs/"
file_path = "./logs/test.log"
Path(dir_path).mkdir(parents=True, exist_ok=True)

f = open(file_path, 'w')
f.close()

logging.basicConfig(filename=file_path,
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
