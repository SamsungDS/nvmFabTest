"""
Module for creating a logger object which
can be used Test Suite wide for logging.

LOG LEVELS:
* logger.trace("A trace message.")
* logger.debug("A debug message.")
* logger.info("An info message.")
* logger.success("A success message.")
* logger.warning("A warning message.")
* logger.error("An error message.")
* logger.critical("A critical message.")

"""

import sys
from loguru import logger

logger.add("./logs/test_{time}.log", enqueue=True, backtrace=True)
logger.add(sys.stdout, colorize=True)
logger.info("Log file created")