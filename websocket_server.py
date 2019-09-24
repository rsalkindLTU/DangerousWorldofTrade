from websock import WebSocketServer

def ws_factory():
    server = WebSocketServer(
        "localhost",
        4502,
    )

    return server

