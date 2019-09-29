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
import watch_dog as dog
from queue import Queue

# This is the main start point for the whole shebang.

if __name__ == "__main__":
    # Load user.json (file path, db update info, etc.)
    guest = user.User('user.json')

    # check database
    db_c = Thread(target=guest.database_check, name='DatabaseCheck')

    # spawn webserver instance
    serv = serve.server_factory()
    serv_t = Thread(target=serv.run, name='WebServer')

    # spawn websocket instance
    guest.websocket_server = wss.ws_factory()
    guest.register_server()

    # watch directory for file changes
    file_queue = Queue()
    wdog_t = Thread(target=dog.Watcher, args=(guest, file_queue,), name='Watchdog')

    # Start all of the threads
    db_c.start()
    serv_t.start()
    wdog_t.start()
    #guest.watchdog.setup_watcher()
    guest.websocket_server.serve_forever()

    # Any blocking action needs to go here.
    input()
    # Shutdown
    db_c.join()

    serv.shutdown()
    serv_t.join()

    wdog_t.join()

    guest.shutdown()
