# this file is managed by lamb. any changes to it will be lost.
routes = {
    "GET": [
        {
            "action": "default.hello",
            "middleware": [],
            "path": "\\/hello\\/(?P<name>.*?)\\/?$"
        },
        {
            "action": "default.ping",
            "middleware": [],
            "path": "\\/ping\\/?$"
        },
        {
            "action": "default.pong",
            "middleware": [
                "test"
            ],
            "path": "\\/pong\\/?$"
        },
        {
            "action": "default.ping",
            "middleware": [
                "authenticated"
            ],
            "path": "\\/authcheck\\/?$"
        }
    ],
    "POST": [
        {
            "action": "default.ping",
            "middleware": [],
            "path": "\\/ping\\/?$"
        },
        {
            "action": "default.pong",
            "middleware": [
                "test"
            ],
            "path": "\\/pong\\/?$"
        },
        {
            "action": "auth.login",
            "middleware": [],
            "path": "\\/login\\/?$"
        },
        {
            "action": "auth.register",
            "middleware": [],
            "path": "\\/register\\/?$"
        }
    ]
}