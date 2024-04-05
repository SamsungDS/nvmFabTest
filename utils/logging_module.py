import logging

logging.basicConfig(filename="/root/nihal223/nvmeof_compliance/logs/test.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)