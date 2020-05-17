##
# {
#     methods: [ "GET" and/or "POST" ]
#     action: controller_class.function
#     middleware: [] # array of middleware class names to apply to the route
# }
##
routes = {
    "/ping": { 
        "methods": [ "GET", "POST" ],
        "action": "default.ping",
        "middleware": []
    },
    "/pong": { 
        "methods": [ "GET", "POST" ],
        "action": "default.pong",
        "middleware": []
    }
}