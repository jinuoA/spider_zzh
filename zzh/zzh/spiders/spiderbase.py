# coding=utf-8

from scrapy import log, Request
from ..scrapy_redis.spiders import RedisCrawlSpider
import traceback
from selenium import webdriver
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import copy
import importlib
import hashlib
from HTMLParser import HTMLParser
import re
import scrapy
import urllib
import MySQLdb
import datetime
import socket
import logging
import sys
from ..getTitle import GetTitle
from ..conf.user_agents import agents
import requests
from lxml import etree
from HTMLParser import HTMLParser
from ..date_format import get_publish_date

reload(sys)
sys.setdefaultencoding("utf-8")

from ..settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWD,
    MYSQL_DB,
    ZZH_LAST_MONITOR_SUBMISSION_URL
)

'''
本爬虫工程将解析部分代码由外面传入

'''


class BasesCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue ()."""
    name = 'zzhbase'
    redis_key = 'basescrawler:rules'

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(BasesCrawler, self).__init__(*args, **kwargs)
        self.connect = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWD,
                                       db=MYSQL_DB,
                                       charset='utf8')
        self.cursor = self.connect.cursor()
        self.ip = self.get_host_ip()
        self.commit_item_flag_list = [0]

    meta = {
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }

    def parse(self, response):

        self.re_connect_mysql()
        self.commit_item_flag_list[0] = 1
        self.url = response.meta['url']
        agent_ip_port = response.meta.get('agent_ip_port', self.ip)
        last_commit = False
        if response.meta['url'] == ZZH_LAST_MONITOR_SUBMISSION_URL:
            yield {'item_title': None, 'agent_ip_port': agent_ip_port, 'commit': 1}
            self.commit_item_flag_list[0] = 0
            last_commit = True
        else:
            # 失败的url存入数据库
            self.save_fail_url_detail(response)

        try:
            dept_id = response.meta['dept_id']
            dept_name_key = response.meta['dept_name_key']
            next_filter = response.meta.get('next_filter', '0')
            func = response.meta['func']
            func = func.encode('utf8')
            try:
                exec (func)
                # 该处的方法提示没有定义无影响, 和外来传入方法名一致即可
                item_list, next_page_url = parse_spider(response, dept_id, dept_name_key)
                for item in item_list:
                    item['agent_ip_port'] = agent_ip_port
                    yield item

                if next_page_url:
                    for next_page in next_page_url:
                        next_page = response.urljoin(next_page)
                        next_filter = bool(int(next_filter))
                        yield Request(next_page, self.parse, meta=response.meta,
                                      dont_filter=next_filter)
            except:
                print(traceback.format_exc())
        except:
            if last_commit:
                pass
            else:
                print(traceback.format_exc())

    def re_connect_mysql(self):
        try:
            self.connect.ping()
        except:
            self.connect = MySQLdb.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWD,
                                           db=MYSQL_DB, charset='utf8')
            self.cursor = self.connect.cursor()

    def save_fail_url_detail(self, response):
        if response.status != 200:
            # 断开mysql将不统计数据
            # self.re_connect_mysql()
            queue_url = response.meta['url']
            spider_url = response.url
            status_code = response.status
            save_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dept_id = response.meta['dept_id']
            dept_name_key = response.meta['dept_name_key']
            sql = """insert into spider_fail_url \
                      (queue_url,spider_url,status_code, save_time,dept_id, dept_name_key)\
                      values(%s,%s,%s,%s,%s, %s);"""
            argsList = (queue_url, spider_url, status_code, save_time, dept_id, dept_name_key)
            self.cursor.execute(sql, argsList)
            self.connect.commit()

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
