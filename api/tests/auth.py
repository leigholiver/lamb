import uuid, json, base64, time
from support.lamb.Test import Test
from support.AuthUtil import AuthUtil
from models.user import user

class auth(Test):
    name = "auth"
    
    def run(self):
        test_user_username = str(uuid.uuid4())
        test_user_password = "hunter2"
        test_user_token = ""

        # auth bad login test
        self.header("auth bad login test")
        rsp = self.postRequest({
            "path":"/login"
        }, {
            "username": "this-user-probably-doesnt-exist-asmdasjdajsdjasdj",
            "password": test_user_password
        })
        expected = {'statusCode': 403, 'body': '"Forbidden"'}
        result = rsp == expected
        self.record(result, expected, rsp)


        # auth register test
        self.header("auth register test")
        rsp = self.postRequest({
            "path":"/register"
        }, {
            "username": test_user_username,
            "password": test_user_password
        })
        result = rsp['statusCode'] == 201 and "token" in rsp['body']
        expected = str("rsp['statusCode'] == 201 and \"token\" in rsp['body']")
        if result:
            test_user_token = json.loads(rsp['body'])['token']
            print("got token: " + test_user_token)
        self.record(result, expected, rsp)


        # auth register existing username test
        self.header("auth register existing username test")
        rsp = self.postRequest({
            "path":"/register"
        }, {
            "username": test_user_username,
            "password": test_user_password
        })
        expected = {'statusCode': 400, 'body': '"Bad Request"'}
        result = rsp == expected
        self.record(result, expected, rsp)
        

        # auth login test
        self.header("auth login test")
        rsp = self.postRequest({
            "path":"/login"
        }, {
            "username": test_user_username,
            "password": test_user_password
        })
        result = rsp['statusCode'] == 200 and "token" in rsp['body']
        expected = str("rsp['statusCode'] == 200 and \"token\" in rsp['body']")
        self.record(result, expected, rsp)


        # auth bad token test
        self.header("auth bad token test")
        rsp = self.getRequest({
            "path":"/authcheck",
            "headers": {
                "token": "not-a-valid-jwt-token-honest"
            }
        })
        expected = {'statusCode': 403, 'body': '"Forbidden"'}
        result = rsp == expected
        self.record(result, expected, rsp)


        # auth good token test
        self.header("auth good token test")
        rsp = self.getRequest({
            "path":"/authcheck",
            "headers": {
                "token": test_user_token
            }
        })
        expected = {'statusCode': 200, 'body': '"pong"'}
        result = rsp == expected
        self.record(result, expected, rsp)


        # auth token userid mismatch test
        self.header("auth token userid mismatch test")
        userid = "this-is-not-a-real-userid-jsdtasjdtnsdtnasdtnn"               
        bad_token = self.goodTokensGoneBad(test_user_token, { 'userid': userid })
        rsp = self.getRequest({
            "path":"/authcheck",
            "headers": {
                "token": bad_token
            }
        })
        expected = {'statusCode': 403, 'body': '"Forbidden"'}
        result = rsp == expected
        self.record(result, expected, rsp)


        # auth expired token test
        self.header("auth expired token test")
        expires = int(time.time() - 86400)
        bad_token = self.goodTokensGoneBad(test_user_token, { 'expires': expires })
        rsp = self.getRequest({
            "path":"/authcheck",
            "headers": {
                "token": bad_token
            }
        })
        expected = {'statusCode': 403, 'body': '"Forbidden"'}
        result = rsp == expected
        self.record(result, expected, rsp)


        print("Deleting test user...")
        users = user.find({"username": test_user_username})
        for u in users:
            u.delete()
            
        return self.successful


    # these tokens will say ANYTHING
    def goodTokensGoneBad(self, good_token, data):
        # decode it
        decodedBytes = base64.b64decode(good_token)
        decodedStr = str(decodedBytes, "utf-8")
        userid, expires, token_hash = decodedStr.split("::")

        # modify it
        if "userid" in data.keys():
            userid = data['userid']
        
        if "expires" in data.keys():
            expires = data['expires']
        
        # wrap it back up
        data = userid + "::" + str(expires) + "::" + token_hash
        encodedBytes = base64.b64encode(data.encode("utf-8"))
        bad_token = str(encodedBytes, "utf-8")

        return bad_token