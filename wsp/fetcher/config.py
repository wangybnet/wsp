# coding=utf-8

import platform

from wsp.utils.config import ensure_int

DEFAULT_DATA_DIR = "C:/ProgramData/WSP/data" if platform.system() == "Windows" else "~/WSP/data"
DEFAULT_TMP_DIR = "C:/ProgramData/WSP/tmp" if platform.system() == "Windows" else "~/WSP/tmp"
DEFAULT_RPC_ADDR = "0.0.0.0:8091"
DEFAULT_DOWNLOADER_CLIENTS = 200
DEFAULT_NO_WORK_SLEEP_TIME = 5
DEFAULT_DOWNLOADER_BUSY_SLEEP_TIME = 1
DEFAULT_TASK_CODE_DIR = "%s/task/code" % DEFAULT_DATA_DIR

class FetcherConfig:

    def __init__(self, **kw):
        self.master_rpc_addr = kw.get("master_rpc_addr")
        assert self.master_rpc_addr is not None, "Must assign the RPC address of master"
        self.downloader_clients = ensure_int(kw.get("downloader_clients", DEFAULT_DOWNLOADER_CLIENTS))
        self.rpc_addr = kw.get("rpc_addr", DEFAULT_RPC_ADDR)
        self.data_dir = kw.get("data_dir", DEFAULT_DATA_DIR)
        self.tmp_dir = kw.get("tmp_dir", DEFAULT_TMP_DIR)
        self.no_work_sleep_time = ensure_int(kw.get("no_work_sleep_time", DEFAULT_NO_WORK_SLEEP_TIME))
        self.downloader_busy_sleep_time = ensure_int(kw.get("downloader_busy_sleep_time", DEFAULT_DOWNLOADER_BUSY_SLEEP_TIME))
        self.task_code_dir = kw.get("task_code_dir", DEFAULT_TASK_CODE_DIR)
