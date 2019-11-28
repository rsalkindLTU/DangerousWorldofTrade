'''
This file wraps the creation of the websocket server
in a single function. This continues to exist
purely for encapsulation purposes.

Dependencies: websock (>=1.0.3)
'''
from websock import WebSocketServer

def ws_factory():
    server = WebSocketServer(
        "localhost",
        4502,
    )

    return server

