#!/usr/bin/python3
'''
This file contains the main startup information and 
scripting for the Elite: Dangerous (name needed). This
file will handle the state of the webserver, websocket-
server, as well as the database check and shutdown.

Basically, it starts here!
'''
from threading import Thread
from multiprocessing import Process
from multiprocessing import Queue as MPQueue
import user
import webserver as serve
import websocket_server as wss
import watch_dog as dog
from queue import Queue
from os import path
import console_io as con

# This is the main start point for the whole shebang.
if __name__ == "__main__":
    # Load user.json (file path, db update info, etc.)
    guest = user.User('user.json')
    if not path.isfile(path.join('.', 'user.json')):
        # Get some user input!
        info = con.startup_info()
        guest.commander_name = info[0]
        guest.ship_range = float(info[1])
        guest.journal_directory = info[2]
        guest.cargo_size = int(info[3])
        guest.dump_info()

    # check database
    db_c = Thread(target=guest.database_check, name='DatabaseCheck', daemon=True)

    # spawn webserver instance
    #serv = serve.server_factory()
    #serv_t = Thread(target=serv.run, name='WebServer', daemon=True)

    # spawn websocket instance
    #guest.websocket_server = wss.ws_factory()
    #guest.register_server()
    #res_t = Thread(target=guest.listen_and_wait, name='WebSocketServer', daemon=True)

    # watch directory for file changes
    wdog_t = Thread(target=dog.Watcher, args=(guest.file_changes_queue, guest.journal_directory,), name='Watchdog', daemon=True)

    # Start all of the threads
    db_c.start()
    #serv_t.start()
    wdog_t.start()
    #res_t.start()
    #guest.watchdog.setup_watcher()
    #guest.websocket_server.serve_forever()

    # Any blocking action needs to go here.
    guest.listen_and_wait() # Block until it receives a stop message.

    # Shutdown
    db_c.join()

    #serv.shutdown()
    #serv_t.join()

    wdog_t.join()
    #res_t.join()

    guest.shutdown()
