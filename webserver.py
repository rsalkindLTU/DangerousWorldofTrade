'''
This file contains classes and functions dedicated to running
a simple http server to hold the html that gets served to the
user.
'''
import http.server

class server(http.server.HTTPServer):
    '''
    Defines a small class instance for our server to run on.
    All it does is serve the page forever.
    '''
    def run(self):
        print("[Web Server] Starting web server. . .")
        print("[Web Server] Visit 'https://localhost:4501/' to view.")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            print("[Web Server] Web server shutting down.")
            self.server_close()

class quiet_handler(http.server.SimpleHTTPRequestHandler):
    '''
    This class exists for the sole purpose of making the 
    http.server stop dumping text into stdout. Should
    probably make this into a log file, but that is on
    the TODO list.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='./web/', **kwargs)
    def log_message(self, format, *args):
        return

def server_factory():
    ''' Return an instance of the webserver '''
    return server(('', 4501), quiet_handler)
