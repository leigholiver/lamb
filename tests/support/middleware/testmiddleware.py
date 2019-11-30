from support.lamb.Middleware import Middleware
from support.AuthUtil import AuthUtil

class testmiddleware(Middleware):
    def process(self, event):

        # authenticated check
        if isinstance(event['queryStringParameters'], dict) and 'authcheck' in event['queryStringParameters'].keys():
            if isinstance(event['headers'], dict) and "token" in event["headers"].keys():
                token = event["headers"]["token"]
                auth_util = AuthUtil()
                if auth_util.getUserFromToken(token) != False:
                    return event
            self.reject()

        # arbitrarily reject with a 403
        if isinstance(event['queryStringParameters'], dict) and 'reject' in event['queryStringParameters'].keys():
            self.reject()

        # reject with a specific status code and message
        if isinstance(event['queryStringParameters'], dict) and 'teapot' in event['queryStringParameters'].keys():
            self.reject(418, '"I\'m a teapot"')

        # inject fields into the event
        event['MiddlewareInjected'] = "This request was passed through ExampleMiddleware"
        
        return event