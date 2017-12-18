# -*- coding: utf-8 -*-
import redis
from json import JSONEncoder

class ConstAssignmentError:
    pass

class MQClient:
    def __setattr__(self, name, value):
        # Assuming that uppercase variable is constant
        if self.__dict__.has_key(name) and name.isupper():
            raise ConstAssignmentError, "can't change const value (%s)" % name
        self.__dict__[name] = value

    def __init__(self, serv, port):
        self.MSG_REALTIME = 1
        self.MSG_CACHED = 2
        self.MSG_SERIALIZABLE = 3
        self.NOTIFY_CHANNEL = 'ClientNotify' # 用于客户端消息分发的频道
        self.NEWCHANNEL_CHANNEL = 'NewChannel' # 有新频道加入(首个频道订阅者会导致频道创建)
        self.REMOVECHANNEL_CHANNEL = 'RemoveChannel' # 频道移除(全部频道订阅者离开)
        self.redis_client = redis.Redis(host = serv, port = port, socket_connect_timeout = 1, socket_keepalive = True)
        self.pubsub_client = self.redis_client.pubsub()

    def publish(self, channels, message, content):
        tmp = channels.split(';')
        json = dict()
        json['message'] = message
        try:
            json['content'] = eval(content)
        except SyntaxError, e:
            json['content'] = content
        success = False
        for channel in tmp:
            if self.redis_client.publish(channel, JSONEncoder().encode(json)) > 0:
                success = True
        return success

    '''
    publish 端使用，message cache 不应使用该接口
    '''
    def client_notify(self, clients, message, content, type):
        if self.MSG_REALTIME == type:
            self.publish(clients, message, content)
            return
        json = dict()
        json['clients'] = clients
        json['type'] = type
        json['message'] = message
        try:
            json['content'] = eval(content)
        except SyntaxError, e:
            json['content'] = content
        self.redis_client.publish(self.NOTIFY_CHANNEL, JSONEncoder().encode(json))

    def set_value(self, key, value):
        try:
            self.redis_client.set(key, value)
        except Exception, e:
            print e

    def get_value(self, key):
        try:
            return self.redis_client.get(key)
        except Exception, e:
            return None

    def subscribe(self, *args):
        self.pubsub_client.subscribe(args)

    def listen(self):
        return self.pubsub_client.listen()

    def parse_message(self, message):
        try:
            channel = message['channel']
            data = eval(message['data'])
            message = data['message']
            content = data['content']

            return True, channel, message, content
        except Exception, e:
            return False, 0, 0, 0

if __name__ == '__main__':
    redis_client = MQClient('192.168.3.201', 38019)
    redis_client.publish('onVifDeviceInfoChannel', 'messagebox', '{"hello":"helloxxxxx"}')
    '''
    redis_client.subscribe(redis_client.NOTIFY_CHANNEL)
    for item in redis_client.listen():
        print item
    '''
