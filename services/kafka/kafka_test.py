#!/usr/bin/env python
# encoding: utf-8

import unittest
from kafka_helper import KafkaHelper

class TestKafka(unittest.TestCase):

    '''
    测试异常，请在不连接Kafka的情况下，调用Kafka API
    '''
    def test_call_api_without_conn(self):
        with self.assertRaises(Exception):
            KafkaHelper.test_call_api_without_conn()

    '''
    测试数据写入
    '''
    def test_write(self):
        self.assertTrue(KafkaHelper.test_write())

    '''
    测试数据读取
    '''
    def test_read(self):
        self.assertTrue(KafkaHelper.test_read())

    '''
    测试写入一批topic不同的数据，每个topic写入多条消息
    '''
    def test_write_topics(self):
        self.assertTrue(KafkaHelper.test_write_topics())

    '''
    测试读取指定的一批topic的数据
    '''
    def test_read_specfic_topics(self):
        self.assertTrue(KafkaHelper.test_read_specfic_topics())

    '''
    统计某个topic的消息数目
    '''
    def test_count_messages(self):
        self.assertTrue(KafkaHelper.test_count_messages())

    '''
    统计topic的种类
    '''
    def test_count_topics(self):
        self.assertTrue(KafkaHelper.test_count_topics())
