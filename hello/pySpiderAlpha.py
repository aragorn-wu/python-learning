import re
import urllib.request
import urllib
from collections import deque

queue = deque()
visited = set()

url = 'http://news.dbanotes.net'
queue.append(url)
cnt = 0
while queue:
    url = queue.popleft()
    visited |= {url}

    print('complete: ' + str(cnt) + ' Crawling <--- ' + url)
    cnt += 1

    try:
        urlop = urllib.request.urlopen(url,timeout=2)
    except:
        continue

    if (('html' not in urlop.getheader('Content-Type')) or (200 != urlop.getcode())):
        continue

    try:
        data = urlop.read().decode('utf-8')
    except:
        continue
    linkre = re.compile('href=\"(.+?)\"')
    for x in linkre.findall(data):
        if 'http' in x and x not in visited:
            queue.append(x)
            print('enqueue --->  ' + x)
