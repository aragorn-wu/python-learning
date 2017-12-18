# -*- coding: UTF-8 -*-

import base64
import json

import sys
import threading

from concurrent.futures import ThreadPoolExecutor

import iputils
import mqclient
# 基线缓存向主动识别提交识别请求
import onvif_client
from camera_config import cameraConfig

RECOGNIZEREQUEST_CHANNEL = 'gdpsInitiativePerception'
RECOGNIZEREQUEST_MESSAGE = 'recognizeRequest'

# 主动识别向基线缓存提交识别结果
RECOGNIZERESULT_CHANNEL = 'gdpsRecognizeResult'
RECOGNIZERESULT_MESSAGE = 'recognizeResult'

# 主动识别向前端提交识别结果
RECOGNIZERESULT_PORTAL_CHANNEL = "onvifDeviceInfoChannel"

# 配置信息通道
RECOGNIZERE_CONFIG = "cameraLoginConfigChannel"

FILE_PATH = "/gdsoft/soft/gdps/perception/scanner/onvif"


class ONVIFService(object):
    def __init__(self, redisip, redisport):
        self.redis_client = mqclient.MQClient(redisip, redisport)
        self._cameraLoginConfigs = dict()
        self._validCameraLoginConfigs = dict()
        self._ranges = iputils.IpRange()
        self.onvif_client = onvif_client.onvifClient(self.redis_client)
        self.pool = ThreadPoolExecutor(max_workers=10)

    def _subscribe(self):
        self.redis_client.subscribe(RECOGNIZERE_CONFIG);
        self.redis_client.subscribe(RECOGNIZEREQUEST_CHANNEL);
        items = self.redis_client.listen()
        for item in items:
            if item['type'] == 'message':
                self._on_messsage(item)

    def _on_messsage(self, message):
        success, channel, message, content = self.redis_client.parse_message(message)
        if success:
            if channel == RECOGNIZEREQUEST_CHANNEL and message == RECOGNIZEREQUEST_MESSAGE:
                future = self.pool.submit(self._handleRecognizeMessage, content)
            elif channel == RECOGNIZERE_CONFIG:
                self._handleCameraConfigMessage(content)

    def _handleRecognizeMessage(self, content):
        if 'ip' in content:
            ip = content['ip']
            print "received query message,will try to query device ", ip
            if self._validCameraLoginConfigs.has_key(ip):
                security = self._validCameraLoginConfigs.get(ip).getSecurity()
                status = self.onvif_client.QueryDeviceBySecurity(ip, security)
                if status != 0:
                    del self._validCameraLoginConfigs[ip]
            else:
                auths = self._getAuthInfosByIp(ip)
                if 'v' in content:
                    brand = content['v']
                    authsByBrand = self._getAuthInfosByBrand(brand);
                    auths.extend(authsByBrand)

                for auth in auths:
                    if auth[0] and auth[1]:
                        status = self.onvif_client.QueryDeviceByUserNameAndPassword(ip, auth[0], auth[1])
                        if status == 0:
                            validAuth = cameraConfig(ip);
                            validAuth.setValidAuth(auth[0], auth[1])
                            self._validCameraLoginConfigs[ip] = validAuth
                            break
                    else:
                        print "userName or password is invalid .will not query the device %s." % (ip)
        else:
            print "received query message,no ip found .not query the device ."

    def _handleCameraConfigMessage(self, content):
        print "received camera configuration %s" % (content)
        try:
            self._cameraLoginConfigs.clear()
            reader = json.JSONDecoder()
            jc = reader.decode(content)
            for c in jc:
                # for c in content:
                mode = c["mode"];
                uncriptedPassword = base64.b64decode(c["password"])
                c["password"] = uncriptedPassword
                self._cameraLoginConfigs[c["ipVentor"]] = c
        except Exception, e:
            print(e)
            print "handle camera config error ."

    def _getAuthInfosByIp(self, ip):
        auths = []
        for item in self._cameraLoginConfigs.keys():
            if iputils.is_ip(item) and item == ip:
                auths.append((self._cameraLoginConfigs[item]["userName"], self._cameraLoginConfigs[item]["password"]))
            elif iputils.isIpRange(item) and iputils.is_ip(ip):
                self._ranges.add_from_string(item)
                if self._ranges.has(ip):
                    auths.append(
                        (self._cameraLoginConfigs[item]["userName"], self._cameraLoginConfigs[item]["password"]))
        return auths

    def _getAuthInfosByBrand(self, brand):
        auths = []
        for item in self._cameraLoginConfigs.keys():
            if item.lower() == brand.lower():
                auths.append((self._cameraLoginConfigs[item]["userName"], self._cameraLoginConfigs[item]["password"]))
        return auths


if __name__ == '__main__':
    print len(sys.argv)
    if len(sys.argv) == 4:
        service = ONVIFService(sys.argv[1], sys.argv[2])
        service._subscribe()
    else:
        print 'Usage: ssdp_client.py mqserver mqport business_ip'
        quit()
    # service = ONVIFService("10.10.17.88", 38019)
    # service._subscribe()
