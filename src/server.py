import logging
import os
import time
import signal
import threading
import _thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


shutdown_requested = False
class RequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        self._request_count = 0
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self._log_request()
        message = os.getenv("MESSAGE", default="M00nF1sh")
        payload = bytes(message, "utf8")

        self.send_response(200)
        self.send_header("Content-Length", len(payload))
        if shutdown_requested:
            self.send_header("Connection", "close")
        self.end_headers()

        # Simulate large response
        time.sleep(3)
        self.wfile.write(payload)

    def log_message(self, *args, **kwargs):
        # disable built-in response logging
        pass

    def _log_request(self):
        current_time = self.date_time_string()
        self._request_count += 1
        logging.info("client_address:{client_address}, request_count:{request_count}, current_time:{current_time}".format(
            client_address=self.client_address, request_count=self._request_count, current_time=current_time))

def sigterm_handler(*args):
    logging.info('Received SIGTERM, gracefully shutdown now')
    global shutdown_requested
    shutdown_requested = True
    _thread.start_new_thread(lambda svc: svc.shutdown(), (httpd,))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, sigterm_handler)

    server_address = ('0.0.0.0', 8080)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    httpd.daemon_threads = False
    httpd.serve_forever()
