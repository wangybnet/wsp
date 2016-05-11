# coding=utf-8

DEFAULT_MASTER_RPC_ADDR = "0.0.0.0:7310"
DEFAULT_MONITOR_SERVER_ADDR = "0.0.0.0:7330"


class MasterConfig:

    def __init__(self, **kw):
        self.master_rpc_addr = kw.get("master_rpc_addr", DEFAULT_MASTER_RPC_ADDR)
        self.monitor_server_addr = kw.get("monitor_server_addr", DEFAULT_MONITOR_SERVER_ADDR)
