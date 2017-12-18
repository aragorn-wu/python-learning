# -*- coding: utf-8 -*-

import re
import logging
import socket
import struct

__ip_pattern = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')


def is_ip(ip):
    if __ip_pattern.match(ip):
        return True
    return False


def ip_to_num(ip):
    num_ip = socket.ntohl(struct.unpack("I", socket.inet_aton(str(ip)))[0])
    return num_ip


def num_to_ip(ip):
    return socket.inet_ntoa(struct.pack("!I", ip))


def isIpRange(ipRange):
    array_range = ipRange.split('-')
    if len(array_range) == 2:
        if (is_ip(array_range[0]) and is_ip(array_range[0])):
            return True
    return False


class IpRange(object):
    def __init__(self):
        self._ranges = {}

    def __str__(self):
        _str = []
        for k, v in self._ranges.items():
            _str.append('{}-{}'.format(num_to_ip(k), num_to_ip(v)))
        return 'IpRange:{}'.format(_str)

    def has(self, ip):
        if is_ip(ip):
            ip_num = ip_to_num(ip)
            for k, v in self._ranges.items():
                if k <= ip_num and ip_num <= v:
                    return True
        return False

    def empty(self):
        return len(self._ranges) == 0

    def add(self, begin, end):
        if is_ip(begin) and is_ip(end):
            num_begin = ip_to_num(begin)
            num_end = ip_to_num(end)
            if num_begin <= num_end:
                if num_begin in self._ranges:
                    if self._ranges[num_begin] < num_end:
                        self._ranges[num_begin] = num_end
                else:
                    self._ranges[num_begin] = num_end
                return True
            else:
                logging.error('IpRange: wrong iprange(%s-%s)', begin, end)
        return False

    def add_from_string(self, str):
        array_range = str.split('-')
        if len(array_range) == 2:
            return self.add(array_range[0], array_range[1])
        elif len(array_range) == 1:
            return self.add(array_range[0], array_range[0])
        else:
            logging.warning('wrong iprange config: %s', str)
        return False

    def delete(self, begin, end):
        if is_ip(begin) and is_ip(end):
            num_begin = ip_to_num(begin)
            num_end = ip_to_num(end)
            if num_begin in self._ranges.items():
                if self._ranges[num_end] == num_end:
                    del self._ranges[num_begin]

    def clear(self):
        self._ranges = {}


if __name__ == '__main__':
    range = IpRange()
    range.add_from_string('192.168.3.1-192.168.3.100')
    print range.has('192.168.3.1')
    print range.has('192.168.3.10')
    print range.has('192.168.3.100')
    print range.has('192.168.3.101')
