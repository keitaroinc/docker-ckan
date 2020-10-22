from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os

PORT = 5000

web_dir = os.path.join(os.path.dirname(__file__))
os.chdir(web_dir)


def run(server_class=ThreadingHTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ("0.0.0.0", PORT)
    httpd = server_class(server_address, handler_class)
    print("Starting maintenance mode")
    httpd.serve_forever()


if __name__ == "__main__":
    run()

