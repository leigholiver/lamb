import sys, os, json, lamb
from support.lamb.Command import Command
from util.HashUtil import HashUtil
from commands.make import make
from commands.tests import tests

class deploy(Command):
    def run(self, data):
        # i just realised that the packages folder isnt even working
        # when i couldnt use passlib or pyjwt, so this is off for now
        # self.packageUpdate()

        maker = make()
        print("Creating terraform files...")
        maker.run(['terraform'])

        print("Compiling routes...")
        maker.run(['routes'])

        if '--skip-tests' not in data:
            print("Running tests...")
            tsts = tests()
            result = tsts.run(lamb.deploy_tests)
            if not result and '--ignore-tests' not in data:
                print("Tests failed, aborting")
                sys.exit(1)


        print("Deploying - 'terraform init'...")
        os.system('terraform init')

        print("Deploying - 'terraform apply'...")
        if '-auto-approve' in data or '-y' in data:
            os.system('terraform apply -auto-approve')
        else:
            os.system('terraform apply')
            

    # update the packages if:
    # - the requirements.txt file has changed
    # - we've never updated the packages
    def packageUpdate(self):
        hasher = HashUtil()
        pkghash = ""
        reqhash = ""
        data_file = {}

        try:
            reqhash = hasher.hashFile(os.path.dirname(os.path.realpath(__file__)) + "/../requirements.txt")
            with open(os.path.dirname(__file__) + '/../pkghash.json', 'r') as infile:
                data_file = json.load(infile)
            pkghash = hasher.hashDir(os.path.dirname(os.path.realpath(__file__)) + "/../package")
        except Exception as e:
            pass
        
        if 'reqhash' in data_file.keys() and 'pkghash' in data_file.keys() and reqhash == data_file['reqhash'] and pkghash == data_file['pkghash']:
            print("Package update not needed...")
        else:
            print("Packaging dependencies...")
            os.system('pip install -r requirements.txt -t api/package')

            # hash the reqs/packages so we can skip unnecessary updates  
            reqhash = hasher.hashFile(os.path.dirname(os.path.realpath(__file__)) + "/../requirements.txt")
            pkghash = hasher.hashDir(os.path.dirname(os.path.realpath(__file__)) + "/../package")
            data_file = {
                'reqhash': reqhash,
                'pkghash': pkghash
            }
            
            with open(os.path.dirname(__file__) + '/../pkghash.json', 'w') as outfile:
                json.dump(data_file, outfile)
