#!/usr/bin/env bash
# -*- coding:utf-8 -*-

# 这个脚本用于启动Fetcher。

bin=`dirname "${BASH_SOURCE-$0}"`
bin=`cd "$bin"; pwd`

home_dir=`cd "$bin"/../; pwd`
$bin/../pyscripts/start-fetcher.py $home_dir $bin/../etc/fetcher.yaml
