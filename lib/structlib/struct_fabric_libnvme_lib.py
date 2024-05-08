import ctypes, sys

sys.path.insert(1, "/root/nihal223/nvmfabtest/")
from src.macros import *


class LIST_NODE(ctypes.Structure):
    _pack_ = 1

LIST_NODE._fields_ = [
                ("next", ctypes.POINTER(LIST_NODE)),
                ("prev", ctypes.POINTER(LIST_NODE)),
                ]

class LIST_HEAD(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("n", LIST_NODE)]

class NVME_FABRIC_OPTIONS(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("cntlid", ctypes.c_bool),
                ("concat", ctypes.c_bool),
                ("ctrl_loss_tmo", ctypes.c_bool),
                ("data_digest", ctypes.c_bool),
                ("dhchap_ctrl_secret", ctypes.c_bool),
                ("dhchap_secret", ctypes.c_bool),
                ("disable_sqflow", ctypes.c_bool),
                ("discovery", ctypes.c_bool),
                ("duplicate_connect", ctypes.c_bool),
                ("fast_io_fail_tmo", ctypes.c_bool),
                ("hdr_digest", ctypes.c_bool),
                ("host_iface", ctypes.c_bool),
                ("host_traddr", ctypes.c_bool),
                ("hostid", ctypes.c_bool),
                ("hostnqn", ctypes.c_bool),
                ("instance", ctypes.c_bool),
                ("keep_alive_tmo", ctypes.c_bool),
                ("keyring", ctypes.c_bool),
                ("nqn", ctypes.c_bool),
                ("nr_io_queues", ctypes.c_bool),
                ("nr_poll_queues", ctypes.c_bool),
                ("nr_write_queues", ctypes.c_bool),
                ("queue_size", ctypes.c_bool),
                ("reconnect_delay", ctypes.c_bool),
                ("tls", ctypes.c_bool),
                ("tls_key", ctypes.c_bool),
                ("tos", ctypes.c_bool),
                ("traddr", ctypes.c_bool),
                ("transport", ctypes.c_bool),
                ("trsvcid", ctypes.c_bool),
                ]
    
class NVME_ROOT(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("config_file", ctypes.c_char_p),
                ("application", ctypes.c_char_p),
                ("hosts", LIST_HEAD),
                ("endpoints", LIST_HEAD),
                ("fp", ctypes.c_void_p), #FILE
                ("log_level", ctypes.c_int),
                ("log_pid", ctypes.c_bool),
                ("log_timestamp", ctypes.c_bool),
                ("modified", ctypes.c_bool),
                ("mi_probe_enabled", ctypes.c_bool),
                ("options", ctypes.POINTER(NVME_FABRIC_OPTIONS)),
                
                ]

class NVME_FABRICS_CONFIG(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("host_traddr", ctypes.c_char_p),
                ("host_iface", ctypes.c_char_p),
                ("queue_size", ctypes.c_int),
                ("nr_io_queues", ctypes.c_int),
                ("reconnect_delay", ctypes.c_int),
                ("ctrl_loss_tmo", ctypes.c_int),
                ("fast_io_fail_tmo", ctypes.c_int),
                ("keep_alive_tmo", ctypes.c_int),
                ("nr_write_queues", ctypes.c_int),
                ("nr_poll_queues", ctypes.c_int),
                ("tos", ctypes.c_int),
                ("keyring", ctypes.c_int),
                ("tls_key", ctypes.c_int),
                ("duplicate_connect", ctypes.c_bool),
                ("disable_sqflow", ctypes.c_bool),
                ("hdr_digest", ctypes.c_bool),
                ("data_digest", ctypes.c_bool),
                ("tls", ctypes.c_bool),
                ("concat", ctypes.c_bool),
                ]

class NVME_HOST(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("entry", LIST_NODE),
                ("subsystems", LIST_HEAD),
                ("r", ctypes.POINTER(NVME_ROOT)),
                ("hostnqn", ctypes.c_char_p),
                ("hostid", ctypes.c_char_p),
                ("dhchap_key", ctypes.c_char_p),
                ("hostsymname", ctypes.c_char_p),
                ("pdc_enabled", ctypes.c_bool),
                ("pdc_enabled_valid", ctypes.c_bool),
               ]
class NVME_SUBSYSTEM(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("entry", LIST_NODE),
                ("ctrls", LIST_HEAD),
                ("namespaces", LIST_HEAD),
                ("h", ctypes.POINTER(NVME_HOST)),
                ("name", ctypes.c_char_p),
                ("sysfs_dir", ctypes.c_char_p),
                ("subsysnqn", ctypes.c_char_p),
                ("model", ctypes.c_char_p),
                ("serial", ctypes.c_char_p),
                ("firmware", ctypes.c_char_p),
                ("subsystype", ctypes.c_char_p),
                ("application", ctypes.c_char_p),
                ("iopolicy", ctypes.c_char_p),
                ]  

   
class NVME_CTRL(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("entry", LIST_NODE),
                ("paths", LIST_HEAD),
                ("namespaces", LIST_HEAD),
                ("s", ctypes.POINTER(NVME_SUBSYSTEM)),
                ("fd", ctypes.c_int),
                ("name", ctypes.c_char_p),
                ("sysfs_dir", ctypes.c_char_p),
                ("address", ctypes.c_char_p),
                ("firmware", ctypes.c_char_p),
                ("model", ctypes.c_char_p),
                ("state", ctypes.c_char_p),
                ("numa_node", ctypes.c_char_p),
                ("queue_count", ctypes.c_char_p),
                ("serial", ctypes.c_char_p),
                ("sqsize", ctypes.c_char_p),
                ("transport", ctypes.c_char_p),
                ("subsysnqn", ctypes.c_char_p),
                ("traddr", ctypes.c_char_p),
                ("trsvcid", ctypes.c_char_p),
                ("dhchap_key", ctypes.c_char_p),
                ("dhchap_ctrl_key", ctypes.c_char_p),
                ("cntrltype", ctypes.c_char_p),
                ("dctype", ctypes.c_char_p),
                ("phy_slot", ctypes.c_char_p),
                ("discovery_ctrl", ctypes.c_bool),
                ("unique_discovery_ctrl", ctypes.c_bool),
                ("discovered", ctypes.c_bool),
                ("persistent", ctypes.c_bool),
                ("cfg", NVME_FABRICS_CONFIG),
                ]

class RDMA(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("qptype", ctypes.c_uint8),
                ("prtype", ctypes.c_uint8),
                ("cms", ctypes.c_uint8),
                ("rsvd3", ctypes.c_uint8 * 5),
                ("pkey", ctypes.c_uint16),
                ("rsvd10", ctypes.c_uint8 * 246),
                ] 

class TCP(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("sectype", ctypes.c_uint8)] 

class NVMF_TSAS(ctypes.Union):
    _pack_ = 1
    _fields_ = [("common", ctypes.c_char * NVMF_TSAS_SIZE),
                ("rdma", RDMA),
                ("tcp", TCP),
                ]
    
class NVMF_DISC_LOG_ENTRY(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("trtype", ctypes.c_uint8),
                ("adrfam", ctypes.c_uint8),
                ("subtype", ctypes.c_uint8),
                ("treq", ctypes.c_uint8),
                ("portid", ctypes.c_uint16),
                ("cntlid", ctypes.c_uint16),
                ("asqsz", ctypes.c_uint16),
                ("eflags", ctypes.c_uint16),
                ("rsvd12", ctypes.c_uint8 * 20),
                ("trsvcid", ctypes.c_char * NVMF_TRSVCID_SIZE),
                ("rsvd64", ctypes.c_uint8 * 192),
                ("subnqn", ctypes.c_char * NVME_NQN_LENGTH),
                ("traddr", ctypes.c_char * NVMF_TRADDR_SIZE),
                ("tsas", NVMF_TSAS),
                ]
    
class NVMF_DISCOVERY_LOG(ctypes.Structure):
    _pack_ = 1
    _fields = [("genctr", ctypes.c_uint64),
                ("numrec", ctypes.c_uint64),
                ("recfmt", ctypes.c_uint16),
                ("rsvd14", ctypes.c_uint8 * 1006),
                ("entries", NVMF_DISC_LOG_ENTRY * 0),
                ]
 
