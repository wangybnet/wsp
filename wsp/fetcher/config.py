# coding=utf-8

from wsp.utils.config import ensure_int

DEFAULT_RPC_ADDR = "0.0.0.0:8091"
DEFAULT_DOWNLOADER_CLIENTS = 200
DEFAULT_NO_WORK_SLEEP_TIME = 5
DEFAULT_DOWNLOADER_BUSY_SLEEP_TIME = 1
DEFAULT_TASK_PROGRESS_REPORT_TIME = 10


class FetcherConfig:

    def __init__(self, home_dir, **kw):
        self.home_dir = home_dir
        self.master_rpc_addr = kw.get("master_rpc_addr")
        assert self.master_rpc_addr is not None, "Must assign the RPC address of master"
        self.downloader_clients = ensure_int(kw.get("downloader_clients", DEFAULT_DOWNLOADER_CLIENTS))
        self.rpc_addr = kw.get("rpc_addr", DEFAULT_RPC_ADDR)
        self.data_dir = kw.get("data_dir", "%s/data" % self.home_dir)
        self.tmp_dir = kw.get("tmp_dir", "%s/tmp" % self.home_dir)
        self.no_work_sleep_time = ensure_int(kw.get("no_work_sleep_time", DEFAULT_NO_WORK_SLEEP_TIME))
        self.downloader_busy_sleep_time = ensure_int(kw.get("downloader_busy_sleep_time", DEFAULT_DOWNLOADER_BUSY_SLEEP_TIME))
        self.task_code_dir = kw.get("task_code_dir", "%s/task_code" % self.data_dir)
        self.task_progress_report_time = kw.get("task_progress_report_time", DEFAULT_TASK_PROGRESS_REPORT_TIME)
