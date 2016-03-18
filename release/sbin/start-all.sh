#!/usr/bin/env bash
#-*- coding:utf-8 -*-

# 这个脚本用于启动所有服务，根据配置文件先启动Master和Web服务，然后启动各个Fetcher。

bin=`dirname "${BASH_SOURCE-$0}"`
bin=`cd "$bin"; pwd`
