import os, time, hashlib, binascii, json, base64

class AuthUtil():
    expires = 86400 # token expiry time in seconds, 86400 = 1 day
    jwt_secret = os.getenv('JWT_SECRET', "ThisIsNotSecretChangeIt!")
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')

    def generatePasswordHash(self, password):
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                self.salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (self.salt + pwdhash).decode('ascii')

    def verifyPasswordHash(self, password, stored_hash):
        salt = stored_hash[:64]
        stored_hash = stored_hash[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                      password.encode('utf-8'), 
                                      salt.encode('ascii'), 
                                      100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_hash

    def generateToken(self, userid):
        expires = int(time.time() + self.expires)
        token = self.jwt_secret + json.dumps({ 'id': userid, 'expires': expires })
        token_hash = self.generatePasswordHash(token)

        data = userid + "::" + str(expires) + "::" + token_hash
        encodedBytes = base64.b64encode(data.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")
        
        return encodedStr
        #return jwt.encode({ 'id': userid, 'expires': (time.time() + self.expires) }, self.jwt_secret, algorithm='HS256').decode('utf-8')

    def verifyToken(self, userid, token):
        #token_obj = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
        token_obj = self.decodeToken(token)
        
        # is token valid?
        if token_obj == False:
            return False
        # does userid match user id in the token?
        if not userid == token_obj['id']:
            return False
        # has the token expired?
        if token_obj['expires'] > time.time():
            return False
        return True

    def getUserFromToken(self, token):
        token_obj = self.decodeToken(token)
        if token_obj == False:
            return False
        return token_obj['id']

    def decodeToken(self, token):
        try:
            decodedBytes = base64.b64decode(token)
            decodedStr = str(decodedBytes, "utf-8")
            userid, expires, token_hash = decodedStr.split("::")
        except:
            return False
        
        og_token = self.jwt_secret + json.dumps({ 'id': userid, 'expires': int(expires) })
        valid = self.verifyPasswordHash(og_token, token_hash)
        if not valid:
            return False
        return({ 'id': userid, 'expires': expires })