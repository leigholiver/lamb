import json

class Controller():
    def respond(self, status, body):
        return {
            'statusCode': status,
            'body': json.dumps(body)
        }