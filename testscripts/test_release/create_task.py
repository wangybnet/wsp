# coding=utf-8

from xmlrpc.client import ServerProxy


if __name__ == "__main__":
    client = ServerProxy("http://192.168.120.181:8090", allow_none=True)
    task_id = client.create_one({"task_config":{"follow": {}, "start_urls": ["http://cfb.bd.gov.cn", "http://www.iie.ac.cn"]}})
    print("Task ID: ", task_id)
    client.start_one(task_id)
