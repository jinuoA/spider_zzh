# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.utils.serialize import ScrapyJSONEncoder

from kafka.client import SimpleClient
from kafka.producer import SimpleProducer
from .zzhtitlematch import TitleMatchMethod
import traceback
import os
import MySQLdb
import time
import datetime
import sched
import traceback

from .settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWD,
    MYSQL_DB
)

#多个机器上执行爬虫 数据统计输入ip+port, 默认是本机ip
class KafkaPipeline(object):
    """
    Publishes a serialized item into a Kafka topic
    :param producer: The Kafka producer
    :type producer: kafka.producer.Producer
    :param topic: The Kafka topic being used
    :type topic: str or unicode
    """

    def __init__(self, producer, topic):
        """
        :type producer: kafka.producer.Producer
        :type topic: str or unicode
        """
        self.producer = producer
        self.topic = topic
        self.encoder = ScrapyJSONEncoder()
        self.tmp_list = []


    def process_item(self, item, spider):
        """
        Overriden method to process the item
        :param item: Item being passed
        :type item: scrapy.item.Item
        :param spider: The current spider being used
        :type spider: scrapy.spider.Spider
        """
        item = dict(item)
        item['time_str'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item_title = item['item_title']
        if item_title:
            msg = self.encoder.encode(item)
            print msg
            self.producer.send_messages(self.topic, msg)
        else:
            pass


    @classmethod
    def from_settings(cls, settings):
        """
        :param settings: the current Scrapy settings
        :type settings: scrapy.settings.Settings
        :rtype: A :class:`~KafkaPipeline` instance
        """
        k_hosts = settings.get('SCRAPY_KAFKA_HOSTS', '127.0.0.1:9092')
        topic = settings.get('SCRAPY_KAFKA_ITEM_PIPELINE_TOPIC', 'data-topic')
        client = SimpleClient(k_hosts)
        producer = SimpleProducer(client)
        return cls(producer, topic)







