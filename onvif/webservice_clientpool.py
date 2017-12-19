import threading

import time
from suds.client import Client


class WSClientPool(object):
    def __init__(self, count, url):
        self.count = count
        self.url = url
        self.mutex = threading.Lock()
        self.clients = dict()
        self._init_clients()

    def _init_clients(self):
        for i in range(0, self.count):
            client = self._init_client()
            key = id(client)
            self.clients[key] = client

    def _init_client(self):
        ws_client = Client(url=self.url)
        return ws_client

    def get_client(self, serviceAddr, security):
        print "thread %s is try to get client pool lock ." % (threading.current_thread().name)
        self.mutex.acquire(10)
        print "thread %s get client pool lock successfully." % (threading.current_thread().name)
        keys = self.clients.keys()
        while len(keys) <= 0:
            keys = self.clients.keys()
            time.sleep(1)

        client = self.clients.pop(keys[0])
        print "thread %s get client successfully." % (threading.current_thread().name)
        self.mutex.release()
        print "thread %s released client pool lock successfully." % (threading.current_thread().name)
        client.set_options(location=serviceAddr)
        client.set_options(wsse=security)
        return client


    def return_client(self, client):
        key = id(client)
        self.clients[key] = client
        print "thread %s returned client successfully." % (threading.current_thread().name)


    def get_size(self):
        return len(self.clients.keys())
