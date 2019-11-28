from support.lamb.Controller import Controller
from support.AuthUtil import AuthUtil
from models.user import user

class auth(Controller):
    def __init__(self):
        self.auth_util = AuthUtil()

    # POST /register
    def register(self, event):
        try:
            name = event['body']['username']
            pw = event['body']['password']
            if name == "" or pw == "":
                raise Exception
            u = user.find({ 'username': name })
            if len(u) > 0:
                raise Exception
        except Exception as e:
            print(e)
            return self.respond(400, "Bad Request")

        pwhash = self.auth_util.generatePasswordHash(pw)
        u = user(name, pwhash)
        u.save()
        token = self.auth_util.generateToken(u.id)
        return self.respond(201, { "id": u.id, "token": token })

    # POST /login
    def login(self, event):
        try:        
            name = event['body']['username']
            pw = event['body']['password']
            if name == "" or pw == "":
                raise Exception

            u = user.find({ 'username': name })
            if len(u) == 1 and self.auth_util.verifyPasswordHash(pw, u[0].password):
                return self.respond(200, { "id": u[0].id, "token": self.auth_util.generateToken(u[0].id) })
            return self.respond(403, "Forbidden")
        except Exception as e:
            print(e)
            return self.respond(400, "Bad Request")       

        return self.respond(500, "Internal Server Error")

