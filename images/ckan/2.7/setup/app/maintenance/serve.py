from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
import os

PORT = 5000

web_dir = os.path.join(os.path.dirname(__file__))
os.chdir(web_dir)

Handler = SimpleHTTPRequestHandler


class MaintenanceServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


if __name__ == "__main__":
    httpd = MaintenanceServer(("0.0.0.0", PORT), Handler) 
    print("Starting maintenance mode")
    httpd.serve_forever()

