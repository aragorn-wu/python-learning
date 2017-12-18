# -*- coding: UTF-8 -*-
import base64
from json import JSONEncoder

from suds.client import Client
from suds.wsse import Security
from suds_passworddigest.token import UsernameDigestToken

from webservice_clientpool import WSClientPool

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


class onvifClient(object):
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.devicemgt_client_pool = WSClientPool(10, 'file://' + FILE_PATH + '/wsdl/devicemgmt.wsdl')
        self.media_client_pool = WSClientPool(10, 'file://' + FILE_PATH + '/wsdl/media.wsdl')

    def QueryDeviceByUserNameAndPassword(self, cameraIp, cameraUserName, cameraPassword):
        security = Security()
        token = UsernameDigestToken(cameraUserName, cameraPassword)
        security.tokens.append(token)

        deviceInfo = dict()
        status = self._getDeviceInformation(cameraIp, security, deviceInfo);
        if status != 0:
            return status
        status = self._getVideoSourcesInfo(cameraIp, security, deviceInfo)
        if status != 0:
            return status
        print deviceInfo
        self.redis_client.publish(RECOGNIZERESULT_PORTAL_CHANNEL, RECOGNIZERESULT_PORTAL_CHANNEL,
                                  JSONEncoder().encode(deviceInfo))
        print "get device info %s successfully .using username %s .password %s" % (
            cameraIp, cameraUserName, cameraPassword)
        return 0

    def QueryDeviceBySecurity(self, cameraIp, security):
        deviceInfo = dict()
        status = self._getDeviceInformation(cameraIp, security, deviceInfo);
        if status != 0:
            return status
        status = self._getVideoSourcesInfo(cameraIp, security, deviceInfo)
        if status != 0:
            return status
        print deviceInfo
        self.redis_client.publish(RECOGNIZERESULT_PORTAL_CHANNEL, RECOGNIZERESULT_PORTAL_CHANNEL,
                                  JSONEncoder().encode(deviceInfo))
        print "get device info %s successfully ." % (cameraIp)
        return 0

    def _getVideoSourcesInfo(self, cameraIp, security, deviceInfo):
        serviceAddr = "http://" + cameraIp + "/onvif/Media"
        dc = self.media_client_pool.get_client(serviceAddr, security)
        print"will get media client .the size of media client is %s" % ( self.media_client_pool.get_size())

        ret = None
        try:
            ret = getattr(dc.service, "GetVideoSources")()
            print "get video info %s successfully ." % (cameraIp)
        except Exception, e:
            print(e)
            print "get video info %s error ." % (cameraIp)
            self.media_client_pool.return_client(dc)
            print"will return media client .the size of media client is %s" % ( self.media_client_pool.get_size())

            return -1
        try:
            deviceInfo["BacklightCompensation"] = ret[0].Imaging.BacklightCompensation.Mode
        except Exception:
            if hasattr(ret[0], "Extension"):
                deviceInfo["BacklightCompensation"] = ret[0].Extension.Imaging[0].BacklightCompensation[0].Mode[0]
        deviceInfo["ResolutionWidth"] = ret[0].Resolution.Width
        deviceInfo["ResolutionHeight"] = ret[0].Resolution.Height

        try:
            ret = getattr(dc.service, "GetVideoEncoderConfigurations")()
            print "get video encoder %s successfully ." % (cameraIp)
            deviceInfo["encoding"] = ret[0].Encoding
        except Exception:
            print "get video encoder %s error ." % (cameraIp)
            self.media_client_pool.return_client(dc)
            print"will return media client .the size of media client is %s" % (self.media_client_pool.get_size())
            return -1
        try:
            ret = getattr(dc.service, "GetAudioSources")()
            print "get audio sources %s successfully ." % (cameraIp)
            deviceInfo["audio"] = "true"
        except Exception:
            print "get audio sources %s failed service not supported." % (cameraIp)
            deviceInfo["audio"] = "false"
        self.media_client_pool.return_client(dc)
        print"will return media client .the size of media client is %s" % (self.media_client_pool.get_size())
        return 0

    def _getDeviceInformation(self, cameraIp, security, deviceInfo):
        serviceAddr = "http://" + cameraIp + "/onvif/device_service"
        dc = self.devicemgt_client_pool.get_client(serviceAddr, security)
        print"will get devicemgt client .the size of devicemgt client is %s" % ( self.devicemgt_client_pool.get_size())

        try:
            ret = getattr(dc.service, "GetDeviceInformation")()
            print "get device info %s successfully ." % (cameraIp)
            deviceInfo['IP'] = cameraIp
            deviceInfo['DeviceName'] = "camera"
            deviceInfo['Manufacturer'] = ret.Manufacturer
            deviceInfo['Model'] = ret.Model
            deviceInfo['DeviceID'] = ret.SerialNumber
        except Exception, e:
            print e
            print "get device info %s error ." % (cameraIp)
            self.devicemgt_client_pool.return_client(dc)
            print"will return devicemgt client .the size of devicemgt client is %s" % (self.devicemgt_client_pool.get_size())

            return 1
        self.devicemgt_client_pool.return_client(dc)
        print"will return devicemgt client .the size of devicemgt client is %s" % (self.devicemgt_client_pool.get_size())

        return 0
