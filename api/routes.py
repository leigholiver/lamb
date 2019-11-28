##
# {
#     methods: [ "GET" and/or "POST" ]
#     action: ControllerClass.function
#     middleware: [] # array of middleware class names to apply to the route
# }
# if you update this file, you must run ./lambctl make routes
##
routes = {
    "/hello/(name)": { 
        "methods": [ "GET" ],
        "action": "default.hello",
        "middleware": [
        ]
    },
    "/ping": { 
        "methods": [ "GET", "POST" ],
        "action": "default.ping",
        "middleware": [
        ]
    },
    "/pong": { 
        "methods": [ "GET", "POST" ],
        "action": "default.pong",
        "middleware": [
            "test"
        ]
    },
    "/authcheck": { 
        "methods": [ "GET" ],
        "action": "default.ping",
        "middleware": [
            "authenticated"
        ]
    },
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