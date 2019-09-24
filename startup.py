#!/usr/bin/python3
'''
This file contains the main startup information and 
scripting for the Elite: Dangerous (name needed). This
file will handle the state of the webserver, websocket-
server, as well as the database check and shutdown.

Basically, it starts here!
'''
from threading import Thread
import user
import webserver as serve
import websocket_server as wss

# This is the main start point for the whole shebang.

if __name__ == "__main__":
    # Load user.json (file path, db update info, etc.)
    guest = user.User('user.json')

    # check database
    db_c = Thread(target=guest.database_check)
    #guest.database_check()

    # spawn webserver instance
    serv = serve.server_factory()
    serv_t = Thread(target=serv.run)

    # spawn websocket instance
    guest.websocket_server = wss.ws_factory()
    guest.register_server()

    # watch directory for file changes
    #guest.load_watcher()

    # Start all of the threads
    db_c.start()
    serv_t.start()
    guest.websocket_server.serve_forever()

    # Any blocking action needs to go here.
    input()
    # Shutdown
    db_c.join()

    serv.shutdown()
    serv_t.join()

    guest.shutdown()
