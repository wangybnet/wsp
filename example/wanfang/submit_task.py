#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import yaml


if __name__ == "__main__":
    config_yaml = {}
    with open("config.yaml", "r", encoding="utf-8") as f:
        config_yaml = yaml.load(f)
    print(config_yaml)
