# coding=utf-8

from wsp.utils.config import ensure_int

DEFAULT_KAFKA_CONSUMER_TIMEOUT_MS = 5000
DEFAULT_MONGO_DB = "wsp"
DEFAULT_MONGO_TASK_TBL = "task"
DEFAULT_MONGO_TASK_CONFIG_TBL = "task_config"
DEFAULT_MONGO_TASK_CONFIG_ZIP = "zip"
DEFAULT_TASK_CODE_DIR = "DEFAULT_DATA_DIR%s" % "/task/code"
DEFAULT_TASK_CONFIG_FILE = "config.yaml"


class SystemConfig:

    def __init__(self, **kw):
        self.kafka_addr = kw.get("kafka_addr", None)
        self.mongo_addr = kw.get("mongo_addr", None)
        self.kafka_consumer_timeout_ms = ensure_int(kw.get("kafka_consumer_timeout_ms", DEFAULT_KAFKA_CONSUMER_TIMEOUT_MS))
        self.mongo_db = kw.get("mongo_db", DEFAULT_MONGO_DB)
        self.mongo_task_tbl = kw.get("mongo_task_tbl", DEFAULT_MONGO_TASK_TBL)
        self.mongo_task_config_tbl = kw.get("mongo_task_config_tbl", DEFAULT_MONGO_TASK_CONFIG_TBL)
        self.mongo_task_config_zip = kw.get("mongo_task_config_zip", DEFAULT_MONGO_TASK_CONFIG_ZIP)
        self.task_code_dir = kw.get("task_code_dir", DEFAULT_TASK_CODE_DIR)
        self.task_config_file = kw.get("task_config_file", DEFAULT_TASK_CONFIG_FILE)
