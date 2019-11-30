##
# {
#     methods: [ "GET" and/or "POST" ]
#     action: ControllerClass.function
#     middleware: [] # array of middleware class names to apply to the route
# }
# if you update this file, you must run ./lambctl make routes
##
routes = {
    "/login": { 
        "methods": [ "POST" ],
        "action": "auth.login",
        "middleware": [
        ]
    },
    "/register": { 
        "methods": [ "POST" ],
        "action": "auth.register",
        "middleware": [
        ]
    }
}