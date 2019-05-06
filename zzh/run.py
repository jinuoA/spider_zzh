# -*-coding:utf-8 -*-
from scrapy import cmdline
import pymysql
import json
import redis

name = 'zzhbase'

cmd = 'scrapy crawl {0}'.format(name)


def input_date():
    con = pymysql.connect(host='192.168.5.125', port=3305, user='root', passwd='root1234', db='url', charset='utf8')
    cur = con.cursor()
    sql = 'select dept_id,dept_name_key,url,func,content_xpath from zzh_projectruler where id>3243'
    cur.execute(sql)
    result = cur.fetchall()
    print len(result)
    for r in result:
        data = {
            "spider": "zzhbase",
            "project": "zzh",
            "dept_id": r[0],
            "dept_name_key": r[1],
            "url": r[2],
            "func": r[3],
            "next_filter": '0',
            "content_xpath": r[4]
        }
        # data = json.dumps(data)
        print data
        reminder_str = json.dumps(data)
        r = redis.StrictRedis(host='192.168.5.127', port=6380, db=0)
        print r.lpush('basescrawler:rules', reminder_str)


# input_date()
cmdline.execute(cmd.split())
