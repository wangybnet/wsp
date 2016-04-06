# coding=utf-8

import asyncio
import time
import logging
from xmlrpc.client import ServerProxy
from pymongo import MongoClient
from bson import ObjectId

from wsp.config import SystemConfig
from ..config import MasterConfig

log = logging.getLogger(__name__)


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
            completed_insc, total_insc = self._update_increament(progress)
            if completed_insc > 0 or total_insc > 0:
                task_id = progress["task_id"]
                tp = self._tasks[task_id]
                obj_id = ObjectId(task_id)
                otp_json = self._task_progress_tbl.find_one({"_id": obj_id})
                if otp_json is None:
                    self._task_progress_tbl.insert_one({"_id": obj_id,
                                                        "completed": tp.completed,
                                                        "total": tp.total,
                                                        "last_modified": tp.last_modified})
                else:
                    otp = _TaskProgress(**otp_json)
                    self._task_progress_tbl.update_one({"_id": obj_id},
                                                       {"$set": {"completed": otp.completed + completed_insc,
                                                                 "total": otp.total + total_insc,
                                                                 "last_modified": tp.last_modified}})

    async def inspect(self):
        await asyncio.sleep(self._inspect_time)
        t = time.time()
        for task_id in [i for i in self._tasks.keys()]:
            log.debug("The task %s has not been updated for %s seconds" % (task_id, int(t - self._tasks[task_id].last_modified)))
            delta_t = t - self._tasks[task_id].last_modified
            if delta_t > self._inspect_time:
                client = ServerProxy(self._master_addr)
                client.finish_task(task_id)
                self._remove_task(task_id)

    """
    更新增量
    """
    def _update_increament(self, progress):
        completed_insc, total_insc = 0, 0
        task_id = progress["task_id"]
        signature = progress["signature"]
        tp = _TaskProgress(**progress)
        if task_id not in self._tasks:
            self._tasks[task_id] = tp
            self._tasks_parts[task_id] = {signature: tp}
            completed_insc, total_insc = tp.completed, tp.total
        else:
            parts = self._tasks_parts[task_id]
            if signature in parts:
                otp = parts[signature]
                if tp.completed >= otp.completed and tp.total >= otp.total:
                    parts[signature] = tp
                    completed_insc, total_insc = tp.completed - otp.completed, tp.total - otp.total
            else:
                parts[signature] = tp
                completed_insc, total_insc = tp.completed, tp.total
            if completed_insc > 0 or total_insc > 0:
                self._tasks[task_id].completed += completed_insc
                self._tasks[task_id].total += total_insc
                self._tasks[task_id].last_modified = tp.last_modified
        return completed_insc, total_insc

    def _remove_task(self, task_id):
        self._tasks.pop(task_id)
        self._tasks_parts.pop(task_id)


class _TaskProgress:
    def __init__(self, **kw):
        self.completed = kw.get("completed", 0)
        self.total = kw.get("total", 0)
        self.last_modified = kw.get("last_modified")
        if self.last_modified is None:
            self.last_modified = time.time()
