#!/usr/bin/python3

import re
import os
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    def __init__(self, user_in, out_queue):
        self.watch_dir = user_in.journal_directory
        self.last_journal = find_current_journal(self.watch_dir)
        self.info_queue = out_queue
        print('[Watchdog] Starting file watchdog. . .')
        self.start()

    def start(self):
        '''
        This function starts the observer instance.
        That's it really.

        NOTE: This function blocks.
        '''
        event_handler = self.MyHandler()
        event_handler.filename = self.last_journal
        observer = Observer()
        observer.schedule(event_handler, path=self.watch_dir, recursive=False)
        observer.daemon = True
        observer.start()
        print("[Watchdog] Observer started.")


    ##### SUBCLASS #####
    class MyHandler(FileSystemEventHandler):
        def __init__(self):
            pass

        def on_modified(self, event):
            super().info_queue.put_nowait(('file_update', event.src_path))

        def on_created(self, event):
            super().info_queue.put_nowait(('file_created', event.src_path))
            #print('[Watchdog] Reading from new journal file (' + str(event.src_path) + ')')
    ##### SUBCLASS END #####


def find_current_journal(directory):
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
