# encoding=utf-8

import socket
import urllib
import urllib.request
import re
from collections import deque

# from queue import Queue

# 保存文件的后缀
import os

PATH_PREFIX = "/tmp/spider/"
SUFFIX = '.html'
# 提取文章标题的正则表达式
REX_TITLE = r'<title>(.*?)</title>'
# 提取所需链接的正则表达式
REX_URL = r'/python/(.+?).html'
# 种子url，从这个url开始爬取
BASE_URL = 'http://www.yiibai.com/python/'


class bdfspider:
    def __init__(self, seeds):
        # self.queue = Queue()
        self.queue = deque()
        self.visited = set()

        if isinstance(seeds, str):
            self.queue.append(seeds)
        if isinstance(seeds, list):
            for i in seeds:
                self.queue.append(i)

    def savefile(self, file_name, file_content):
        if os.path.exists(PATH_PREFIX) == False:
            os.mkdir(PATH_PREFIX)

        with open(PATH_PREFIX+file_name.replace('/', '_')+SUFFIX, "w") as f:
            f.write(file_content)

    def gettitle(self, file_content):
        linkre = re.search(REX_TITLE, file_content)
        if linkre:
            return linkre.group(1)

    def getlink(self, html_content):
        linkre = re.compile(REX_URL)
        for sub_link in linkre.findall(html_content):
            sub_url = BASE_URL + sub_link + SUFFIX

            if sub_url in self.visited:
                pass
            else:
                self.queue.append(sub_url)
                print('加入队列 ---> ' + sub_url)

    def crawling(self):
        while self.queue:
            url = self.queue.popleft()
            if url in self.visited:
                continue


            self.visited.add(url)
            print("正在抓取 <--- " + url)
            urlop = urllib.request.urlopen(url)

            data = urlop.read().decode('utf-8')
            title = self.gettitle(data)
            self.savefile(title, data)
            self.getlink(data)



spider = bdfspider(BASE_URL)
spider.crawling()
