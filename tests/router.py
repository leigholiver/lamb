from support.lamb.Test import Test
from support.AuthUtil import AuthUtil
from models.user import user

class router(Test):
    name = "router"
    def run(self):

        # ping test
        self.header("ping test")
        rsp = self.getRequest({
            "path":"/ping"
        })
        expected = {'statusCode': 200, 'body': '"pong"'}
        result = rsp == expected
        self.record(result, expected, rsp)

        # 404 not found test
        self.header("404 not found test")
        rsp = self.getRequest({
            "path":"/sdtstsdtasdtasdkfjasidfasdf-doesnt-exist-zzzzzzzz"
        })
        expected = {'statusCode': 404, 'body': '"Not Found"'}
        result = rsp == expected
        self.record(result, expected, rsp)


        # middleware injection test
        self.header("middleware injection test")
        rsp = self.getRequest({
            "path":"/pong"
        })
        result = rsp['statusCode'] == 200 and "MiddlewareInjected" in rsp['body']
        expected = str("rsp['statusCode'] == 200 and \"\"MiddlewareInjected\"\" in rsp['body']")
        self.record(result, expected, rsp)


        # middleware reject test
        self.header("middleware reject test")
        rsp = self.getRequest({
            "path":"/pong",
            "queryStringParameters": { 'reject': 1 }
        })
        expected = {'statusCode': 403, 'body': '"Forbidden"'}
        result = rsp == expected
        self.record(result, expected, rsp)


        # middleware custom reject test
        self.header("middleware reject test")
        rsp = self.getRequest({
            "path":"/pong",
            "queryStringParameters": { 'teapot': 1 }
        })
        expected = {'statusCode': 418, 'body': '"I\'m a teapot"'}
        result = rsp == expected
        self.record(result, expected, rsp)
    

        # post ping test
        self.header("POST ping test")
        rsp = self.postRequest({
            "path":"/ping"
        }, {})
        expected = {'statusCode': 200, 'body': '"pong"'}
        result = rsp == expected
        self.record(result, expected, rsp)

        # route parameters test
        self.header("route parameters test")
        rsp = self.getRequest({
            "path":"/hello/john"
        })
        expected = {'statusCode': 200, 'body': '"hello, john"'}
        result = rsp == expected
        self.record(result, expected, rsp)

        # middelware authentication tests
        test_user_username = "test-user"
        test_user_password = "hunter2"
        auth_util = AuthUtil()
        pwhash = auth_util.generatePasswordHash(test_user_password)
        test_user = user(test_user_username, pwhash)
        test_user_token = auth_util.generateToken(test_user.id)

        self.header("no token middleware authentication test")
        rsp = self.getRequest({
            "path":"/pong",
            "queryStringParameters": { 'authcheck': 1 }
        })
        expected = {'statusCode': 403, 'body': '"Forbidden"'}
        result = rsp == expected
        self.record(result, expected, rsp)

        self.header("bad token middleware authentication test")
        rsp = self.getRequest({
            "path":"/pong",
            "queryStringParameters": { 'authcheck': 1 },
            "headers": { "token": "this-is-a-bad-token" }
        })
        expected = {'statusCode': 403, 'body': '"Forbidden"'}
        result = rsp == expected
        self.record(result, expected, rsp)

        self.header("good token middleware authentication test")
        rsp = self.getRequest({
            "path":"/pong",
            "queryStringParameters": { 'authcheck': 1 },
            "headers": { "token": test_user_token }
        })
        print(rsp)
        expected = "'statusCode': 200"
        result = rsp['statusCode'] == 200
        self.record(result, expected, rsp)

        return self.successful