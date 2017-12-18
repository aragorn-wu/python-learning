import base64

from suds.wsse import Security
from suds_passworddigest.token import UsernameDigestToken


class cameraConfig():
    def __init__(self, ip):
        self.ip = ip
        self.validUserName = ''
        self.validPassword = ''
        self.security = Security();
        self.authorizations = []

    def _addNewAuthorition(self, userName, password):
        conrainStatus = False
        for auth in self.authorizations:
            if auth[0] == userName and auth[1] == password:
                conrainStatus = True
                break
        if not conrainStatus:
            configTup = (userName, password)
            self.authorizations.append(configTup)
            print "device %s added username %s and new password %s ." % (self.ip, userName, password)

    def _disableAuthorization(self):
        self.validUserName = ''
        self.validPassword = ''
        self.security = None

    def setValidAuth(self, userName, password):
        self._addNewAuthorition(userName, password)
        self.validUserName = userName
        self.validPassword = password

        token = UsernameDigestToken(self.validUserName, password)
        self.security.tokens.append(token)

    def getAuthorizationStatus(self):
        if self.validUserName.strip() == '' and self.validPassword.strip() == '':
            return False
        return True

    def getAuthorizationInfo(self):
        return self.validUserName, self.validPassword

    def getSecurity(self):
        return self.security
