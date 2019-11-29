import uuid, json, base64, time
from support.lamb.Test import Test
from support.AuthUtil import AuthUtil
from models.user import user

class auth(Test):
    name = "auth"

    def __init__(self):
        self.auth_util = AuthUtil()
    
    def run(self):
        test_user_username = str(uuid.uuid4())
        test_user_password = "hunter2"
        test_user_token = ""
        test_user = None

        # generate and verify a pwhash
        self.header("generate/verify password hash")
        pwhash = self.auth_util.generatePasswordHash(test_user_password)
        result = self.auth_util.verifyPasswordHash(test_user_password, pwhash)
        self.record(result == True, "True", str(result))

        # create a test user
        test_user = user(test_user_username, pwhash)
        test_user.save()

        # generate and verify a token
        self.header("generate/verify authentication token")
        test_user_token = self.auth_util.generateToken(test_user.id)
        userid = self.auth_util.getUserFromToken(test_user_token)
        self.record(test_user.id == userid, str(test_user.id), str(userid))

        # bad token
        self.header("bad token")
        result = self.auth_util.getUserFromToken("this-isnt-a-real-token")
        self.record(result == False, "False", str(result))

        # expired token
        self.header("expired token")
        expires = int(time.time() - 86400)
        bad_token = self.goodTokensGoneBad(test_user_token, { 'expires': expires })
        result = self.auth_util.getUserFromToken(bad_token)
        self.record(result == False, "False", str(result))
        
        # userid mismatch
        self.header("token userid mismatch")
        bad_token = self.goodTokensGoneBad(test_user_token, { 'userid': "not-a-real-userid" })
        result = self.auth_util.getUserFromToken(bad_token)
        self.record(result == False, "False", str(result))

        print("Deleting test user(s)...")
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