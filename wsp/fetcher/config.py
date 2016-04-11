# coding=utf-8

DEFAULT_RPC_ADDR = "0.0.0.0:8091"


class FetcherConfig:

    def __init__(self, home_dir, **kw):
        self.home_dir = home_dir
        self.master_rpc_addr = kw.get("master_rpc_addr")
        assert self.master_rpc_addr is not None, "Must assign the RPC address of master"
        self.rpc_addr = kw.get("rpc_addr", DEFAULT_RPC_ADDR)
        self.data_dir = kw.get("data_dir", "%s/data" % self.home_dir)
        self.tmp_dir = kw.get("tmp_dir", "%s/tmp" % self.home_dir)
        self.task_code_dir = kw.get("task_code_dir", "%s/task_code" % self.data_dir)
