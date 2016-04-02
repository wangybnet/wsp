#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import yaml
import zipfile
from xmlrpc.client import ServerProxy, Binary


if __name__ == "__main__":
    config_yaml = {}
    with open("config.yaml", "r", encoding="utf-8") as f:
        config_yaml = yaml.load(f)
    print(config_yaml)
    zipf = "wanfang.zip"
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED) as fz:
        fz.write("config.yaml")
        for root, dirs, files in os.walk("project"):
            for file in files:
                fz.write("%s/%s" % (root, file))
    with open(zipf, "rb") as f:
        zipb = f.read()
    client = ServerProxy("http://192.168.120.181:7310", allow_none=True)
    task_id = client.create_one({"desc": "万方数据"}, Binary(zipb))
    print("Task ID: ", task_id)
    client.start_one(task_id)
