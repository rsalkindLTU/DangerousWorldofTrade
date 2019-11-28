'''
This file details a class that wraps functionality around
a 'user'. When startup occurs, a user is created and the 
functions inside of here are used to keep track of 
information that may be floating around.

External Dependencies: requests (>=2.22.0), websock (>=1.0.3),
    watchdog (>=0.9.0)
Author: Rhys Salkind
License: todo.
'''

import os
import sys
import queue
import json
from datetime import datetime
from db import gen, DBHandler
from multiprocessing import Queue as MPQueue
import live_db_operations as ldb
from concurrent.futures import ThreadPoolExecutor
import console_io as con

pool = ThreadPoolExecutor(3)

class User:
    def __init__(self, filename = ''):
        '''
        Creates the framework for all of initial information for use 
        in the class for later. Also checks the directory for a user.json
        file and loads it if present.
        '''

        self.journal_directory = ''
        self.current_journal = ''
        self.db_check = 0.1 # A timestamp. If longer than 7 days, you gotta get the entire database downloaded.

        self.commander_name = ''
        self.cargo_size = 0
        self.location = (None, None, None)
        self.range = 0

        self.state = 'startup'

        self.message_queue = queue.Queue() # Queue for posting messages to the websocket client
        #self.file_queue = queue.Queue() # Queue object for receiving information from the file watchdog
        self.client_input_queue = queue.Queue() # Queue object for the client to communicate w/ the server.

        self.file_changes_queue         = MPQueue() # A queue for noting file changes, AKA the queue for the watchdog
        self.message_from_client_queue  = queue.Queue() # A queue for receiving messages from the client
        self.message_from_server_queue  = queue.Queue() # A queue for sending messages to the server.

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
            self.cargo_size         = js['cargo_size']
            self.location           = js['location']
            self.ship_range         = js['range']
        else:
            # Do nothing
            print("[Load User] No 'user.json' file found, running blind!")
            return

    def set_state(self, new_state):
        '''
        Updates the internal state of the self.state variable
        and posts a message to the message file_queue to tell
        others what has occured. May be removed in the future.
        '''
        old_state = self.state
        self.state = new_state
        js = {
            'event': 'state_update',
            'old_state': old_state,
            'new_state': new_state
        }
        self.file_changes_queue.put(json.dumps(js))

    def insert_message(self, message):
        ''' Inserts a message into the message_queue '''
        self.message_queue.put(message)

    def database_check(self):
        '''
        A wrapper function used to check the database file that the
        user will need. Generates the entire database again if the
        user does not have it.
        '''
        # Get the current time stamp out
        print("[Database Check] Checking database. . .")
        self.set_state("database_check")
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
            if self.location != (None, None, None):
                ldb.build_distances(self.location)
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
        self.set_state("ready")
        self.dump_info() # Write contents to file

    def shutdown(self):
        '''
        A wrapper function to hold all shutdown procedures (such
        as clearing queues and posting the shutdown to the client)
        '''
        self.dump_info()

    def dump_info(self):
        '''
        Writes data to a user.json file to save state over
        multiple running multiple instances of the file.
        '''
        out = {}

        out['journal_directory']    = self.journal_directory
        out['current_journal']      = self.current_journal
        out['db_check']             = self.db_check

        out['commander_name']       = self.commander_name
        out['cargo_size']           = self.cargo_size
        out['location']             = self.location
        out['range']                = self.ship_range

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
        print('[Web Socket Server] Web Socket Server is ready.')
        #self.websocket_server.on_server_destruct = pass

    def handle_websocket_input(self, client, data):
        '''
        Websocket handler function. Helps handle data coming from
        the client to the user.
        '''
        print("Client sent: '{}'".format(data))
        if data == 'shutdown':
            self.websocket_server.close_server()
            #sys.exit(0)

    def register_client(self, client):
        '''
        Websocket function handler. Called when a new client 
        connects to the server.
        '''
        print("[Web Socket Server] Client registered.")
        self.client = client
        msg = "Hello there!"
        self.send_to_client(msg)
        #self.listen_and_wait()

    def log_websocket_error(self, exception):
        '''
        Websocket handler. Called when the websocket
        encounters an error.
        '''
        print("[Web Socket Server] Exception: (" + exception + ")")
        print("[Web Socket Server] Continuing. . .")

    def unregister_client(self, client):
        '''
        Websocket handler. Called when the client decides 
        to disconnect from the server.
        '''
        # Reset client to none as the client has disconnected.
        print("[Web Socket Server] Client has disconnected.")
        self.client = None

    def send_to_client(self, msg):
        '''
        This function wraps the act of sending a message
        to the client. It will queue messages that have
        attempted to send when the client is not connected,
        and will send them with the newest message once
        the client has connected.
        '''
        if self.client == None:
            # Enqueue the message for later
            self.message_queue.put(msg)
            return

        temp = None
        try:
            temp = self.message_queue.get_nowait()
        except:
            pass


        print("Temp is: {}".format(temp))
        if temp is not None:
            # send all the messages from the queue
            while 1:
                print("SENDING : {}".format(temp))
                self.websocket_server.send(self.client, temp)
                try:
                    temp = self.message_queue.get_nowait()
                except:
                    break

        print("SENDING : {}".format(msg))
        self.websocket_server.send(self.client, msg)

    def listen_and_wait(self):
        '''
        Function will read items from the watchdog queue
        and determine what needs to be sent over the websocket.

        The watchdog queue is self.file_changes_queue
        The websocket queue is self.message_queue
        '''
        # Wait for a message from the filestore
        file_offset = 0

        value = 500000
        last_cargo = None #self.grab_current_cargo()

        new_message = ''
        last_message = ''
        while 1:
            # blocks until it grabs a message
            message = self.file_changes_queue.get()
            if message == last_message:
                continue

            if message[0] == 'file_update':
                # [1] is going to be the full file path
                # We have to handle what the file is too.
                msg_filepath = message[1].split('\\')[-1] # Grab just the filename
                #print("MSG_FILEPATH: {}".format(msg_filepath))

                # Check if the update message was from cargo.json or from market.json
                # If it is cargo.json, we know the cargo and 'value' that it holds
                # If it is market.json, we know where the player currently is docked, and can log that.

                if msg_filepath.lower() == 'cargo.json':
                    print("[Cargo Check] Checking cargo. . .")
                    value, last_cargo = self.cargo_file_handler(message[1], value, last_cargo)
                    print("[Cargo Check] Done.")
                if msg_filepath.lower() == 'market.json':
                    new_message = self.market_file_handler(message[1], value)

            if new_message != '':
                self.send_to_client(new_message)
                # else pass

            last_message = message

    def market_file_handler(self, filepath, spend_limit):
        '''
        This function takes in a market.json file and updates the players
        current location and the cargo values. 
        '''
        # Get the json into a dict
        while 1:
            try:
                with open(filepath, 'r') as f:
                    js = json.load(f)
                star_system = js['StarSystem']
                station_name = js['StationName']
                break
            except:
                # Try again until the file actually exists
                pass

        # Create a DBHandler instance to get the location of the star system
        db_conn = DBHandler()
        out = db_conn.request("SELECT x, y, z FROM systems WHERE name = ?", (star_system,))

        #print('Market db request returned {}'.format(out))

        if self.location != list(out[0]):
            self.location = list(out[0])
            self.dump_info()
            print('[Market Check] New location, rebuilding distance table. . .')
            ldb.build_distances(self.location)
            print('[Market Check] Done.')

        # Setup the database thread to run in the background
        future = pool.submit(ldb.planets_in_range, self.ship_range, self.location, self.cargo_size, station_name, spend_limit)
        # Set up the call back for the future.
        future.add_done_callback(con.next_location_to_buy)

        print('[Market Check] Looking for goods to trade. . .')

    def cargo_file_handler(self, filepath, spend_limit, last_cargo):
        '''
        This function takes in a filepath, spending limit, and a cargo
        and determines if the limit needs to increase or the cargo
        needs to be updated.
        '''
        # For now, cut this out. We're not using it
        return spend_limit, last_cargo
        # From the cargo file, determine what will be sold and 

        next_cargo = self.grab_current_cargo()

        # First case: No cargo -> Cargo
        # spend_limit remains the same, last_cargo updates.
        print('[Cargo Check] Last cargo is {}'.format(last_cargo))
        print('[Cargo Check] Next cargo is {}'.format(next_cargo))

        # If they are the same, nothing has changed. Return.
        if next_cargo == last_cargo:
            return spend_limit, last_cargo


        if last_cargo == None or last_cargo == []:
            return spend_limit, next_cargo

        # Second case: Cargo -> No Cargo
        # spend_limit will increase depending on what the value of the cargo
        # was at the location that it gets sold, last_cargo becomes next_cargo.
        if next_cargo == None or next_cargo == []:
            # Grab the station name that we are at
            db_conn = DBHandler()
            station_name = None
            while 1:
                try:
                    print('[Cargo Check] Opening cargo.json. . .')
                    with open(filepath, 'r') as f:
                        js = json.load(f)
                    station_name = js['StationName']
                    break
                except:
                    # Try again until the file actually exists
                    continue

            print('[Cargo Check] Station Name is {}'.format(station_name))

            # Get the station ID
            station_id = db_conn.request("SELECT id FROM stations WHERE name = ?", (station_name,))

            # Get the commodity id for the current cargo.
            cargo_ids = []
            for item in last_cargo:
                cargo_ids.append(db_conn.request("SELECT id FROM commodities WHERE name = ?", (item,)))

            # Grab the sell value at for the cargo id's at the station id
            for item in cargo_ids:
                profit = db_conn.request(
                    "SELECT sell_price FROM listings WHERE station_id = ? AND commodity_id = ?", 
                    (station_id, item,)
                )
                spend_limit += profit

            # Return!
            return spend_limit, next_cargo

    def grab_current_cargo(self):
        '''
        Using the watch directory, return the inventory from the cargo file.
        '''
        while 1:
            print('[Cargo Grab] Trying to grab cargo. . .')
            try:
                with open(os.path.join(self.journal_directory, 'Cargo.json'), 'r') as f:
                    js = json.load(f)
                break
            except:
                pass

        try:
            return js['Inventory']
        except:
            return []

