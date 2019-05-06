#-*- coding:utf -*-
import random
import requests
from lxml import etree
from multiprocessing import Pool
from .conf.user_agents import agents
class GetTitle():
    def getTit(self,url,title_xpath):
        page = requests.get(url,headers={'User-Agent': random.choice(agents)})
        page.encoding = 'utf-8'
        page = page.text
        page = etree.HTML(page)
        try:
            title = page.xpath(title_xpath)
            title = title[0]
            return title
        except:
            title = ''
            return title