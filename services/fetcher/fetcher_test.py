#!/usr/bin/env python
# encoding: utf-8

import unittest
from fetcher_helper import FetcherHelper

class TestFetcher(unittest.TestCase):

    '''
    测试下载一个网页（非gzip）
    '''
    def test_download_page(self):
        FetcherHelper.test_download_page()

    '''
    测试下载一个网页（gzip）
    '''
    def test_download_gzip(self):
        FetcherHelper.test_download_gzip()

    '''
    测试下载一张图片
    '''
    def test_download_image(self):
        FetcherHelper.test_download_image()

    '''
    测试异步下载一批网页（使用gevent框架）
    '''
    def test_download_async(self):
        FetcherHelper.test_download_async()

    '''
    测试连接fetcher的RPC服务，并向其发送数据
    '''
    def test_conn_rpc(self):
        FetcherHelper.test_conn_rpc()

    '''
    测试连接kafka
    '''
    def test_conn_kafka(self):
        FetcherHelper.test_conn_kafka()

    '''
    测试从kafka中无限循环取指定topic的数据（topic可能有多个）
    '''
    def test_loop_fetch(self):
        FetcherHelper.test_loop_fetch()

    '''
    测试从kafka中无限循环取指定topic的数据，并使用RPC发送增加某topic订阅的命令
    '''
    def test_loop_fetch_and_add(self):
        FetcherHelper.test_loop_fetch_and_add()

    '''
    测试从kafka中无限循环取指定topic的数据，并使用RPC发送取消某topic订阅的命令
    '''
    def test_loop_fetch_and_cancel(self):
        FetcherHelper.test_loop_fetch_and_cancel()

