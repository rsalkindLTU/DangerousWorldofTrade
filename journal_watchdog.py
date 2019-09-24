#!/usr/bin/python3

# All this file does is send a message when a journal file for 
# Elite Dangerous is updated.

import os
from time import sleep
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.filename = ''
    def on_modified(self, event):
        if event.src_path == (working_dir + '\\' + self.filename):
            print("File (" + str(event.src_path) + ") has changed.")

    def on_created(self, event):
        print('Reading from new journal file (' + str(event.src_path) + ')')
        temp = event.src_path
        ind = temp.find('\\', 28)
        self.filename = temp[len(temp) - ind + 2:]
        print(self.filename)

working_dir = """C:\\Users\\rsalkind\\Saved Games\\Frontier Developments\\Elite Dangerous"""

def find_current_journal(directory):
    # List all .log files in the directory
    logs = os.listdir(directory)
    # Filter out all non-log files
    new_logs = []
    for l in logs:
        if re.search(r"\w*\.log$", l):
            new_logs.append(l)

    logs = new_logs

    # Get the current date to try to match the timestamp
    #date = datetime.now().date()
    #print(logs[::-1])
    logs = logs[::-1]
    print("Found current journal at '" + str(logs[0]) + "'")
    print("Watching that file. . . ")
    wait_and_notify(logs[0])

def wait_and_notify(filename):
    filepath = os.path.join(working_dir, filename)
    event_handler = MyHandler()
    event_handler.filename = filename
    observer = Observer()
    observer.schedule(event_handler, path=working_dir, recursive=False)
    observer.start()

    try:
        while 1:
            sleep(1)
    except KeyboardInterrupt:
            observer.stop()
    observer.join()

find_current_journal(working_dir)
