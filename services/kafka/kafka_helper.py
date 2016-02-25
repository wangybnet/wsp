#!/usr/bin/env python
# encoding: utf-8

class KafkaHelper(object):

    '''
    测试异常，请在不连接Kafka的情况下，调用Kafka API
    '''
    @staticmethod
    def test_call_api_without_conn():
        raise Exception

    '''
    测试数据写入
    '''
    @staticmethod
    def test_write():
        return 'message'

    '''
    测试数据读取
    '''
    @staticmethod
    def test_read():
        return 'message'

    '''
    测试写入一批topic不同的数据，每个topic写入多条消息
    '''
    @staticmethod
    def test_write_topics():
        return 'many topics'

    '''
    测试读取指定的一批topic的数据
    '''
    @staticmethod
    def test_read_specfic_topics():
        return 'many topics'

    '''
    统计某个topic的消息数目
    '''
    @staticmethod
    def test_count_messages():
        return 3

    '''
    统计topic的种类
    '''
    @staticmethod
    def test_count_topics():
        return 3
