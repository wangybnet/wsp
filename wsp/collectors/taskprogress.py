# coding=utf-8

import asyncio
import time
import logging
from xmlrpc.client import ServerProxy
from pymongo import MongoClient
from bson import ObjectId

from wsp.config import SystemConfig, MasterConfig

log = logging.getLogger(__name__)


class TaskProgressCollector:

    def __init__(self, sys_config, local_config):
        assert isinstance(sys_config, SystemConfig) and isinstance(local_config, MasterConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._local_config = local_config
        self._inspect_time = self._sys_config.task_progress_inspect_time
        master_addr = self._local_config.master_rpc_addr
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
        log.debug("Handle data: %s" % progress_list)
        if not progress_list:
            return
        for progress in progress_list:
            completed_insc, total_insc = self._update_increment(progress)
            log.debug("Task %s, completed increment: %s, total increment: %s" % (progress["task_id"], completed_insc, total_insc))
            if completed_insc > 0 or total_insc > 0:
                try:
                    self._update_database(progress["task_id"], completed_insc, total_insc)
                except Exception:
                    log.warning("Unexpected error occurred when handling data", exc_info=True)

    async def inspect(self):
        await asyncio.sleep(self._inspect_time)
        for task_id in [i for i in self._tasks.keys()]:
            if not self._tasks[task_id].updated:
                log.debug("The task %s has not been updated in the last %s seconds" % (task_id, self._inspect_time))
                with ServerProxy(self._master_addr) as client:
                    client.finish_task(task_id)
                self._tasks.pop(task_id)
                self._tasks_parts.pop(task_id)
            else:
                self._tasks[task_id].updated = False

    """
    更新增量
    """
    def _update_increment(self, progress):
        completed_insc, total_insc = 0, 0
        task_id = progress["task_id"]
        signature = progress["signature"]
        tp = _TaskProgress(**progress, updated=True)
        if task_id not in self._tasks_parts:
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
            if task_id not in self._tasks:
                self._tasks[task_id] = _TaskStatus()
            self._tasks[task_id].updated = True
        return completed_insc, total_insc

    """
    更新数据库
    """
    def _update_database(self, task_id, completed_insc, total_insc):
        obj_id = ObjectId(task_id)
        otp_json = self._task_progress_tbl.find_one({"_id": obj_id})
        if otp_json is None:
            self._task_progress_tbl.insert_one({"_id": obj_id,
                                                "completed": completed_insc,
                                                "total": total_insc,
                                                "last_modified": time.time()})
        else:
            self._task_progress_tbl.update_one({"_id": obj_id},
                                               {"$inc": {"completed": completed_insc,
                                                         "total": total_insc}})
            self._task_progress_tbl.update_one({"_id": obj_id},
                                               {"$set": {"last_modified": time.time()}})


class _TaskProgress:

    def __init__(self, **kw):
        self.completed = kw.get("completed", 0)
        self.total = kw.get("total", 0)
        self.updated = kw.get("updated", False)


class _TaskStatus:

    def __init__(self):
        self.updated = False
