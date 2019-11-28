import time, json, re
from routes_compiled import routes
from support.Rejection import Rejection

def lambda_handler(event, context):
    #t_start = time.time()
    router = Router()
    #t_boot = time.time()
    response = router.respond(event, context)
    #t_response = time.time()
    # print("boot: " + str(t_boot - t_start) + ", response: " + str(t_response - t_boot))
    return response

class Router():
    def respond(self, event, context):
        try:
            if 'httpMethod' not in event.keys() or 'path' not in event.keys():
                return {
                    'statusCode': 400,
                    'body': '"Bad Request"'
                }

            if event['httpMethod'] in routes.keys():
                for route in routes[event['httpMethod']]:
                    match = re.search(route['path'], event['path'])
                    if (match):
                        route_params = match.groupdict()
                        route_params['event'] = event

                        controller, dot, function = route['action'].partition(".")
                        if 'middleware' in route.keys():
                            for mwname in route['middleware']:
                                mw = getattr(getattr(__import__("middleware." + mwname), mwname), mwname)
                                mw = mw()
                                try:
                                    event = mw.process(event)
                                except Rejection as e:
                                    return {
                                        'statusCode': e.statusCode,
                                        'body': e.body
                                    }

                        ctrlr = getattr(getattr(__import__("controllers." + controller), controller), controller)
                        ctrlr = ctrlr()
                        action = getattr(ctrlr, function)

                        if "body" in event.keys() and event['body'] != None:
                            try:
                                event['body'] = json.loads(event['body'])
                            except:
                                pass
                                
                        return action(**route_params)
            return {
                'statusCode': 404,
                'body': '"Not Found"'
            }

        except Exception as e:
            raise e
            return {
                'statusCode': 500,
                'body': '"Internal Server Error"'
            }