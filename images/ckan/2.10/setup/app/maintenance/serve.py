"""
Copyright (c) 2016 Keitaro AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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

