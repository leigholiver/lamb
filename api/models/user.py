from support.lamb.Model import Model

class user(Model):
    def __init__(self, username="", password=""):
        super(user, self).__init__()
        self.username = username
        self.password = password
        
        # the name of the dynamodb table 
        self.table = "user"

        # list of str, fields which are allowed
        # to be updated from the api
        self.fillable = []

        # list of fields to use as string 
        # indexes you will be able to use 
        # these as parameters for user.find()
        self.indexes = [ 'username' ]