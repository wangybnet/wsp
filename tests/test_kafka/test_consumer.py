# coding=utf-8

import logging

from kafka.consumer import KafkaConsumer


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)

    consumer = KafkaConsumer("wangybnet",
                             auto_offset_reset='earliest',
                             bootstrap_servers=['192.168.120.90:9092'])
    for message in consumer:
        print("message:", message.value)
