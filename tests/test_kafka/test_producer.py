# coding=utf-8

import logging

from kafka.producer import KafkaProducer


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)

    producer = KafkaProducer(bootstrap_servers=["192.168.120.90:9092"])
    producer.send("wangybnet", b"Hello, World!")
