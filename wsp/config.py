# coding=utf-8

import re


class MasterConfig:
    DEFAULT_MASTER_RPC_ADDR = "0.0.0.0:7310"
    DEFAULT_MONITOR_SERVER_ADDR = "0.0.0.0:7330"

    def __init__(self, **kw):
        self.master_rpc_addr = kw.get("master_rpc_addr", self.DEFAULT_MASTER_RPC_ADDR)
        self.monitor_server_addr = kw.get("monitor_server_addr", self.DEFAULT_MONITOR_SERVER_ADDR)


class FetcherConfig:
    DEFAULT_FETCHER_RPC_ADDR = "0.0.0.0:7320"

    def __init__(self, **kw):
        self.master_rpc_addr = kw.get("master_rpc_addr")
        assert self.master_rpc_addr is not None, "Must assign the RPC address of master"
        self.fetcher_rpc_addr = kw.get("fetcher_rpc_addr", self.DEFAULT_FETCHER_RPC_ADDR)
        self.fetcher_dir = kw.get("fetcher_dir")
        assert self.fetcher_dir is not None, "Must assign the directory that the fetcher uses"
        self.task_code_dir = kw.get("task_code_dir", "%s/task_code" % self.fetcher_dir)


class SystemConfig:
    DEFAULT_MONGO_DB = "wsp"
    DEFAULT_MONGO_TASK_TBL = "task"
    DEFAULT_MONGO_TASK_PROGRESS_TBL = "task_progress"
    DEFAULT_MONGO_TASK_CONFIG_TBL = "task_config"
    DEFAULT_TASK_CONFIG_FILE = "config.yaml"
    DEFAULT_KAFKA_CONSUMER_TIMEOUT_MS = 5000
    DEFAULT_DOWNLOADER_CLIENTS = 100
    DEFAULT_DOWNLOADER_TIMEOUT = 20
    DEFAULT_NO_WORK_SLEEP_TIME = 5
    DEFAULT_TASK_PROGRESS_REPORT_TIME = 10
    DEFAULT_TASK_PROGRESS_INSPECT_TIME = 300

    def __init__(self, **kw):
        self.kafka_addr = kw.get("kafka_addr")
        assert self.kafka_addr is not None, "Must assign the address of Kafka"
        self.mongo_addr = kw.get("mongo_addr")
        assert self.mongo_addr is not None, "Must assign the address of MongoDB"
        self.monitor_server_addr = kw.get("monitor_server_addr")
        assert self.monitor_server_addr is not None, "Must assign the address of monitor server"
        self.mongo_db = kw.get("mongo_db", self.DEFAULT_MONGO_DB)
        self.mongo_task_tbl = kw.get("mongo_task_tbl", self.DEFAULT_MONGO_TASK_TBL)
        self.mongo_task_progress_tbl = kw.get("mongo_task_progress_tbl", self.DEFAULT_MONGO_TASK_PROGRESS_TBL)
        self.mongo_task_config_tbl = kw.get("mongo_task_config_tbl", self.DEFAULT_MONGO_TASK_CONFIG_TBL)
        self.task_config_file = kw.get("task_config_file", self.DEFAULT_TASK_CONFIG_FILE)
        self.kafka_consumer_timeout_ms = kw.get("kafka_consumer_timeout_ms", self.DEFAULT_KAFKA_CONSUMER_TIMEOUT_MS)
        self.downloader_clients = kw.get("downloader_clients", self.DEFAULT_DOWNLOADER_CLIENTS)
        self.downloader_timeout = kw.get("downloader_timeout", self.DEFAULT_DOWNLOADER_TIMEOUT)
        self.no_work_sleep_time = kw.get("no_work_sleep_time", self.DEFAULT_NO_WORK_SLEEP_TIME)
        self.task_progress_report_time = kw.get("task_progress_report_time", self.DEFAULT_TASK_PROGRESS_REPORT_TIME)
        self.task_progress_inspect_time = kw.get("task_progress_inspect_time", self.DEFAULT_TASK_PROGRESS_INSPECT_TIME)


class TaskConfig:
    TASK_ID = "task_id"
    START_URLS = "start_urls"
    DOWNLOADER_MIDDLEWARES = "downloader_middlewares"
    SPIDER_MIDDLEWARES = "spider_middlewares"
    SPIDERS = "spiders"

    def __init__(self, **kw):
        self._config = dict(kw)

    def get(self, name, default=None):
        res = self._config.get(name)
        if res is None:
            return default
        return res

    def setdefault(self, name, value):
        self._config.setdefault(name, value)

    def __getitem__(self, item):
        return self._config.get(item)

    def __setitem__(self, key, value):
        self._config[key] = value


class AgentConfig:
    DEFAULT_AGENT_SERVER_ADDR = "0.0.0.0:7350"
    DEFAULT_PROXY_QUEUE_SIZE = 10000
    DEFAULT_BACK_QUEUE_SIZE = 1000000

    class Page:

        def __init__(self, url, page=None):
            self.urls = []
            if page:
                start, end = page.split("-")
                start, end = int(start), int(end)
                i = start
                while i <= end:
                    self.urls.append(url.replace("[page]", str(i)))
                    i += 1
            else:
                self.urls.append(url)

    class Match:

        def __init__(self, url_match, proxy_match):
            self._url_match = re.compile(url_match)
            self._proxy_match = re.compile(proxy_match.encode("utf-8"))

        def findall(self, url, body):
            res = []
            if self._url_match.search(url):
                for i in self._proxy_match.findall(body):
                    if isinstance(i, tuple):
                        res.append("%s:%s" % (i[0].decode("utf-8"), i[1].decode("utf-8")))
                    else:
                        res.append(i.decode("utf-8"))
            return res

    class Test:

        def __init__(self, url, timeout=20, search=None):
            self.url = url
            self.timeout = timeout
            self._url_match, self._body_match = None, None
            if search:
                if "url" in search:
                    self._url_match = re.compile(search["url"])
                if "body" in search:
                    self._body_match = re.compile(search["body"].encode("utf-8"))

        def match(self, url, body):
            if self._url_match and not self._url_match.search(url):
                return False
            if self._body_match and not self._body_match.search(body):
                return False
            return True

    def __init__(self, **kw):
        start_pages = kw.get("start_pages", [])
        if not isinstance(start_pages, list):
            start_pages = [start_pages]
        self.start_pages = [self.Page(**i) for i in start_pages]
        update_pages = kw.get("update_pages", [])
        if not isinstance(update_pages, list):
            update_pages = [update_pages]
        self.update_pages = [self.Page(**i) for i in update_pages]
        proxy_rules = kw.get("proxy_rules", [])
        if not isinstance(proxy_rules, list):
            proxy_rules = [proxy_rules]
        self.proxy_match = [self.Match(**i) for i in proxy_rules]
        http_test = kw.get("http_test", [])
        if not isinstance(http_test, list):
            http_test = [http_test]
        self.http_test = [self.Test(**i) for i in http_test]
        self.agent_dir = kw.get("agent_dir")
        assert self.agent_dir is not None, "Must assign the directory that the agent uses"
