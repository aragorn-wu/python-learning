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

    def _add_authorition(self, userName, password):
        conrainStatus = False
        for auth in self.authorizations:
            if auth[0] == userName and auth[1] == password:
                conrainStatus = True
                break
        if not conrainStatus:
            configTup = (userName, password)
            self.authorizations.append(configTup)
            print "device %s added username %s and new password %s ." % (self.ip, userName, password)

    def _disable_authorization(self):
        self.validUserName = ''
        self.validPassword = ''
        self.security = None

    def set_valid_auth(self, userName, password):
        self._add_authorition(userName, password)
        self.validUserName = userName
        self.validPassword = password

        token = UsernameDigestToken(self.validUserName, password)
        self.security.tokens.append(token)

    def get_authorization_status(self):
        if self.validUserName.strip() == '' and self.validPassword.strip() == '':
            return False
        return True

    def get_authorization_info(self):
        return self.validUserName, self.validPassword

    def get_security(self):
        return self.security
