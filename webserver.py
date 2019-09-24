'''
This file contains classes and functions dedicated to running
a simple http server to hold the html that gets served to the
user.
'''
import http.server

class server(http.server.HTTPServer):
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
    def log_message(self, format, *args):
        return

def server_factory():
    return server(('', 4501), quiet_handler)
