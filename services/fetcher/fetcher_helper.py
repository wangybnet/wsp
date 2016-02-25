#!/usr/bin/env python
# encoding: utf-8

class FetcherHelper(object):

    '''
    测试下载一个网页（非gzip）
    '''
    @staticmethod
    def test_download_page():
        return 'page'

    '''
    测试下载一个网页（gzip）
    '''
    @staticmethod
    def test_download_gzip():
        return 'decoded page'

    '''
    测试下载一张图片
    '''
    @staticmethod
    def test_download_image():
        return 'binary image'

    '''
    测试异步下载一批网页（使用gevent框架）
    '''
    @staticmethod
    def test_download_async():
        return 'many pages'

    '''
    测试连接fetcher的RPC服务，并向其发送数据
    '''
    @staticmethod
    def test_conn_rpc():
        return 'send ok'

    '''
    测试连接kafka
    '''
    @staticmethod
    def test_conn_kafka():
        return 'ok'

    '''
    测试从kafka中无限循环取指定topic的数据（topic可能有多个）
    '''
    @staticmethod
    def test_loop_fetch():
        return 'topics'

    '''
    测试从kafka中无限循环取指定topic的数据，并使用RPC发送增加某topic订阅的命令
    '''
    @staticmethod
    def test_loop_fetch_and_add():
        return 'new topics'

    '''
    测试从kafka中无限循环取指定topic的数据，并使用RPC发送取消某topic订阅的命令
    '''
    @staticmethod
    def test_loop_fetch_and_cancel():
        return 'new topics'
