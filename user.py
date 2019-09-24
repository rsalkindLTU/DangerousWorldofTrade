import os
import queue
import json
from datetime import datetime
from db import gen

class User:
    def __init__(self, filename = ''):
        self.journal_directory = ''
        self.current_journal = ''
        self.db_check = 0.1 # A timestamp. If longer than 7 days, you gotta get the whole chihuahua.

        self.commander_name = ''
        self.ship_loadout = {}
        self.location = (None, None, None)

        self.state = 'startup'
        self.message_queue = queue.Queue() # Queue for posting json messages from the journal file
        self.websocket_server = None # An object representing a websocket server
        self.client = None # An object representing the websocket client (our html/dart part)
        self.confirm = True # An object used to confirm a response

        if filename != '':
            self.parse_from_file(filename)

    def parse_from_file(self, filename):
        '''
        This function will take a file name for a file that
        may not exist. If it does, it will load the relevant
        info into the class. If it does not, nothing will happen.
        '''
        print("[Load User] Loading user from file. . .")

        if os.path.exists(filename):
            f = open(filename, 'r')
            js = json.load(f)
            f.close()

            self.journal_directory  = js['journal_directory']
            self.current_journal    = js['current_journal']
            self.db_check           = js['db_check']

            self.commmander_name    = js['commander_name']
            self.ship_loadout       = js['ship_loadout']
            self.location           = js['location']
        else:
            # Do nothing
            print("[Load User] No 'user.json' file found, running blind!")
            return

    def insert_message(self, message):
        self.message_queue.put_nowait(message)

    def database_check(self):
        # Get the current time stamp out
        print("[Database Check] Checking database. . .")
        self.state = "databaseCheck"
        try:
            ts = datetime.fromtimestamp(self.db_check)
        except (TypeError, AttributeError): # If no db_timestamp, oooooooooooooooooof.
            # Clean the entire database
            print("[Database Check] Generating entire database.")
            print("[Database Check] This may take a while depending on how fast your internet is.")
            print("[Database Check] The program needs to download ~4GB worth of data :(")
            gen(force_new=True)

            print("[Database Check] Done checking database.")
            self.db_check = datetime.timestamp(datetime.now())
            self.state = "ready"
            return

        # Check if it has been more than 7 days
        current_ts = datetime.now()
        delta = current_ts - ts
        #print('[Database Check] Delta days: ' + str(delta.days))
        if delta.days > 7 or os.path.isfile('universe.db') is False:
            # Clean the entire database
            print("[Database Check] Generating entire database.")
            print("[Database Check] This may take a while depending on how fast your internet is.")
            print("[Database Check] The program needs to download ~4GB worth of data :(")
            gen(force_new=True)
            self.db_check = datetime.timestamp(datetime.now())
        elif delta.days > 1:
            # Only partially clean the database
            # if the delta is greater than one day
            print("[Database Check] Regenerating part of the database.")
            print("[Database Check] This may take a while depending on how fast your internet is.")
            print("[Database Check] The program needs to download ~350MB worth of data :(")
            gen()
            self.db_check = datetime.timestamp(datetime.now())

        print("[Database Check] Done checking database.")
        self.state = "ready"
        self.dump_info() # Write contents to file

    def shutdown(self):
        '''
        Clean up when shutting down.
        '''
        self.dump_info()

    def dump_info(self):
        '''
        Write data to the file to keep things orderly.
        '''
        out = {}

        out['journal_directory']    = self.journal_directory
        out['current_journal']      = self.current_journal
        out['db_check']             = self.db_check

        out['commander_name']       = self.commander_name
        out['ship_loadout']         = self.ship_loadout
        out['location']             = self.location

        with open('user.json', 'w') as f:
            json.dump(out, f)

    def register_server(self):
        '''
        Takes self.websocket_server and gets it ready for use
        '''
        self.websocket_server.on_data_receive       = self.handle_websocket_input
        self.websocket_server.on_connection_open    = self.register_client
        self.websocket_server.on_error              = self.log_websocket_error
        self.websocket_server.on_connection_close   = self.unregister_client
        #self.websocket_server.on_server_destruct = pass

    def handle_websocket_input(self, client, data):
        if self.client == client:
            # parse the data here.
            pass
        pass

    def register_client(self, client):
        print("[Web Socket Server] Client registered.")
        self.client = client

    def log_websocket_error(self, exception):
        print("[Web Socket Server] Exception: (" + exception + ")")
        print("[Web Socket Server] Continuing. . .")

    def unregister_client(self, client):
        # Reset client to none as the client has disconnected.
        print("[Web Socket Server] Client has disconnected.")
        self.client = None

def user_consumer(user):
    while 1:
        # Block until a user message is seen
        item = user.message_queue.get()
        continue # do nothing for now

