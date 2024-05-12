from http.server import BaseHTTPRequestHandler

import copydetect
import instagrapi
import numpy as np


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(str(np.random.choice([1, 2, 3, 4, 5, 6])).encode())
        return
