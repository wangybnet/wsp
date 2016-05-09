# coding=utf-8

DEFAULT_RPC_ADDR = "0.0.0.0:8091"


class FetcherConfig:

    def __init__(self, **kw):
        self.master_rpc_addr = kw.get("master_rpc_addr")
        assert self.master_rpc_addr is not None, "Must assign the RPC address of master"
        self.rpc_addr = kw.get("rpc_addr", DEFAULT_RPC_ADDR)
        self.fetcher_dir = kw.get("fetcher_dir")
        assert self.fetcher_dir is not None, "Must assign the directory that the fetcher uses"
        self.task_code_dir = kw.get("task_code_dir", "%s/task_code" % self.fetcher_dir)
