from support.lamb.Middleware import Middleware
from support.AuthUtil import AuthUtil

class authenticated(Middleware):
    def process(self, event):
        if isinstance(event['headers'], dict) and "token" in event["headers"].keys():
            token = event["headers"]["token"]
            auth_util = AuthUtil()
            if auth_util.getUserFromToken(token) != False:
                return event
        self.reject()