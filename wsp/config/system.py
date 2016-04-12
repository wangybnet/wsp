# coding=utf-8

from wsp.utils.config import ensure_int

DEFAULT_MONGO_DB = "wsp"
DEFAULT_MONGO_TASK_TBL = "task"
DEFAULT_MONGO_TASK_PROGRESS_TBL = "task_progress"
DEFAULT_MONGO_TASK_CONFIG_TBL = "task_config"
DEFAULT_TASK_CONFIG_FILE = "config.yaml"
DEFAULT_KAFKA_CONSUMER_TIMEOUT_MS = 5000
DEFAULT_DOWNLOADER_CLIENTS = 200
DEFAULT_DOWNLOADER_TIMEOUT = 20
DEFAULT_NO_WORK_SLEEP_TIME = 5
DEFAULT_TASK_PROGRESS_REPORT_TIME = 10
DEFAULT_TASK_PROGRESS_INSPECT_TIME = 300


class SystemConfig:

    def __init__(self, **kw):
        self.kafka_addr = kw.get("kafka_addr")
        assert self.kafka_addr is not None, "Must assign the Kafka address"
        self.mongo_addr = kw.get("mongo_addr")
        assert self.mongo_addr is not None, "Must assign the MongoDB address"
        self.monitor_addr = kw.get("monitor_addr")
        assert self.monitor_addr is not None, "Must assign the Monitor address"
        self.mongo_db = kw.get("mongo_db", DEFAULT_MONGO_DB)
        self.mongo_task_tbl = kw.get("mongo_task_tbl", DEFAULT_MONGO_TASK_TBL)
        self.mongo_task_progress_tbl = kw.get("mongo_task_progress_tbl", DEFAULT_MONGO_TASK_PROGRESS_TBL)
        self.mongo_task_config_tbl = kw.get("mongo_task_config_tbl", DEFAULT_MONGO_TASK_CONFIG_TBL)
        self.task_config_file = kw.get("task_config_file", DEFAULT_TASK_CONFIG_FILE)
        self.kafka_consumer_timeout_ms = ensure_int(kw.get("kafka_consumer_timeout_ms", DEFAULT_KAFKA_CONSUMER_TIMEOUT_MS))
        self.downloader_clients = ensure_int(kw.get("downloader_clients", DEFAULT_DOWNLOADER_CLIENTS))
        self.downloader_timeout = kw.get("downloader_timeout", DEFAULT_DOWNLOADER_TIMEOUT)
        self.no_work_sleep_time = ensure_int(kw.get("no_work_sleep_time", DEFAULT_NO_WORK_SLEEP_TIME))
        self.task_progress_report_time = kw.get("task_progress_report_time", DEFAULT_TASK_PROGRESS_REPORT_TIME)
        self.task_progress_inspect_time = kw.get("task_progress_inspect_time", DEFAULT_TASK_PROGRESS_INSPECT_TIME)
