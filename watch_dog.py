#!/usr/bin/python3

'''
File: watch_dog.py
Description: A file wrapping the watch-dog functionallity
into a single class, which can be used to communicate
with the current user class.

Contains: Watcher (class), find_current_journal (method).
Requirements: watchdog (0.9.0)
'''

import re
import os
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    '''
    Class defining the operations of a watchdog entity
    that will watch the journal file location for changes.
    This allows us to parse through where the player is 
    and pass information to the client.

    External Dependencies: watchdog(0.9.0)
    '''
    def __init__(self, out_queue, journal_dir):
        '''
        Constructor object for the Watcher class. Marks the directory,
        a reference to the user, and starts the watchdog object.
        '''
        self.watch_dir = journal_dir
        self.last_journal = find_current_journal(self.watch_dir)
        self.info_queue = out_queue
        #self.user_reference = user_in
        print('[Watchdog] Starting file watchdog. . .')
        print('[Watchdog] Watching ' + self.last_journal + '. . .')
        self.start()

    def start(self):
        '''
        This function starts the observer instance.
        That's it really.

        NOTE: This function blocks.
        '''
        event_handler = self.MyHandler(self.info_queue)
        event_handler.filename = self.last_journal
        observer = Observer()
        observer.schedule(event_handler, path=self.watch_dir, recursive=False)
        observer.start()
        print("[Watchdog] Observer started.")

    def update_log_file(self, filename):
        '''
        Helper function to update which log file is the current
        log file if a new one is created while the user is playing
        the game.
        '''
        self.last_journal = filename
        #self.user_reference.current_journal = filename
        #self.user_reference.dump_info()
        message = ("journal_file_changed", filename)
        self.info_queue.put(message)

    ##### SUBCLASS #####
    class MyHandler(FileSystemEventHandler):
        '''
        Watchdog handler overload to add functionality. Tells us when
        specific watchdog events happen
        '''
        def __init__(self, out_queue):
            '''
            Initialize the watcher. 
            '''
            #self.watcher = watcher
            self.output_queue = out_queue

        def on_modified(self, event):
            '''
            Function called when something in the file directory changes.
            '''
            self.output_queue.put_nowait(('file_update', event.src_path))
            #self.watcher.info_queue.put_nowait(('file_update', event.src_path))
            # Log the contents of the updated file to a log file
            with open(event.src_path, 'r') as r_target:
                with open('file_logger.log', 'a') as f:
                    f.write("============ {} UPDATED ============ \n".format(event.src_path))
                    f.write(r_target.read())
                    f.write("============ END UPDATE ============ \n")

            #print('File {} updated.'.format(event.src_path))

        def on_created(self, event):
            '''
            Called when any file is created in the directory.
            '''
            self.output_queue.put_nowait(('file_created', event.src_path))
            #self.watcher.info_queue.put_nowait(('file_created', event.src_path))
            print('[Watchdog] A new file has been created: {}'.format(event.src_path))
            filename = os.path.basename(event.src_path)

            # The use of the log file has been depricated :(
            #if filename.endswith('.log'):
                #self.watcher.update_log_file(find_current_journal(filename))

            #print('[Watchdog] Reading from new journal file (' + str(event.src_path) + ')')
    ##### SUBCLASS END #####


def find_current_journal(directory):
    '''
    Helper function used to grab the most recent log file in the
    journal directory of log files.
    '''
    # List all .log files in the directory
    logs = os.listdir(directory)
    # Filter out all non-log files
    new_logs = []
    for l in logs:
        if re.search(r"\w*\.log$", l):
            new_logs.append(l)

    logs = new_logs

    logs = logs[::-1]
    return logs[0]
