""" File containing all macros for constants used throughout the Test Suite """

KATO_ZERO                   = 0
KATO_DEFAULT                = 120000
KATO_NONZERO                = 60000
ASCII_MIN                   = 0x20
ASCII_MAX                   = 0x7E
NVME_DISCOVERY_NQN          = 'nqn.2014-08.org.nvmexpress.discovery'
INVALID_HOSTNQN             = \
    'nqn.2014-08.org.nvmexpress:uuid:THIS_IS_CLEARLY_INVALID'
NVME_NQN_LENGTH				= 256
NVMF_TRADDR_SIZE			= 256
NVMF_TSAS_SIZE				= 256
NVME_DISC_SUBSYS_NAME       = "nqn.2014-08.org.nvmexpress.discovery"
NVMF_TRSVCID_SIZE           = 32
OFFSETS_64BIT = [0, 0x28, 0x30, 0x48, 0x50] 
OFFSET_CONTROLLER_CONFIGURATION = 0x14