# coding=utf-8

import asyncio
import time
from xmlrpc.client import ServerProxy

from pymongo import MongoClient
from bson import ObjectId

from wsp.config import SystemConfig
from ..config import MasterConfig


class TaskProgressMonitor:

    def __init__(self, sys_config, local_config):
        assert isinstance(sys_config, SystemConfig) and isinstance(local_config, MasterConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._local_config = local_config
        self._inspect_time = self._local_config.task_progress_inspect_time
        master_addr = self._local_config.rpc_addr
        colon = master_addr.rindex(":")
        self._master_addr = "http://127.0.0.1%s" % master_addr[colon:]
        self._mongo_client = MongoClient(self._sys_config.mongo_addr)
        self._task_progress_tbl = self._mongo_client[self._sys_config.mongo_db][self._sys_config.mongo_task_progress_tbl]
        self._tasks = {}
        self._tasks_parts = {}

    """
    处理采集的数据
    """
    def handle_data(self, data, addr):
        progress_list = data.get("task_progress")
        if not progress_list:
            return
        for progress in progress_list:
            pulled_insc, pushed_insc = self._update_increament(progress)
            if pulled_insc > 0 or pushed_insc > 0:
                task_id = progress["task_id"]
                self._tasks[task_id].pulled_count += pulled_insc
                self._tasks[task_id].pushed_count += pushed_insc
                tp = self._tasks[task_id]
                obj_id = ObjectId(task_id)
                self._task_progress_tbl.update_one({"_id": obj_id},
                                                   {"$set": {"_id": obj_id,
                                                             "completed": tp.pulled_count,
                                                             "total": tp.pushed_count,
                                                             "last_modified": tp.last_modified}},
                                                   upsert=True)

    async def inspect(self):
        await asyncio.sleep(self._inspect_time)
        t = time.time()
        for task_id in self._tasks.keys():
            if t - self._tasks[task_id] > self._inspect_time:
                self._remove_task(task_id)
                client = ServerProxy("http://127.0.0.1")
                client.finish_task(task_id)

    """
    更新增量
    """
    def _update_increament(self, progress):
        pulled_insc, pushed_insc = 0, 0
        task_id = progress["task_id"]
        signature = progress["signature"]
        if task_id not in self._tasks:
            tp = _TaskProgress(**progress)
            self._tasks[task_id] = tp
            self._tasks_parts[task_id] = {signature: tp}
            pulled_insc, pushed_insc = tp.pulled_count, tp.pushed_count
        else:
            tp = self._tasks[task_id]
            parts = self._tasks_parts[task_id]
            if signature in parts:
                otp = parts[signature]
                if tp.pulled_count >= otp.pulled_count and tp.pushed_count >= otp.pushed_count:
                    parts[signature] = tp
                    pulled_insc, pushed_insc = tp.pulled_count - otp.pulled_count, tp.pushed_count - otp.pushed_count
            else:
                parts[signature] = tp
                pulled_insc, pushed_insc = tp.pulled_count, tp.pushed_count
        return pulled_insc, pushed_insc

    def _remove_task(self, task_id):
        self._tasks.pop(task_id)
        self._tasks_parts.pop(task_id)


class _TaskProgress:

    def __init__(self, **kw):
        self.pulled_count = kw.get("pulled_count", 0)
        self.pushed_count = kw.get("pushed_count", 0)
        self.last_modified = kw.get("last_modified")
        if self.last_modified is None:
            self.last_modified = time.time()
