import os
import platform
import time
import urllib.parse
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import logging


class Sensor:
    target_addr = '10.10.10.1'
    sleep_time = 5

    def __init__(self, _target_addr: str=None):
        logging.basicConfig(level=logging.INFO, format='[IOT][%(asctime)s][%(levelname)s] %(message)s')
        logging.info('starting basic version...')

        hostName = "localhost"
        serverPort = 8090

        self.supervisor()
        logging.debug('after')
        server = HTTPServer((hostName, serverPort), self.Server)
        logging.info("Server started http://%s:%s" % (hostName, serverPort))

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        server.server_close()
        logging.info("Server stopped.")

    def send_data(self, data: bytes):
        params = urllib.parse.urlencode({'data': data})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        try:
            conn = HTTPConnection(self.target_addr, 80, timeout=.1)
            conn.request("POST", "/", params, headers)
            resp = conn.getresponse()
            logging.debug(resp.status)
            logging.debug(resp.read())
        except TimeoutError:
            logging.debug('timed-out')
        finally:
            logging.debug('preceding')

    def fetch_data(self):
        try:
            conn = HTTPConnection(self.target_addr, 80, timeout=5)
            conn.request("GET", "/")
            resp = conn.getresponse()
            logging.debug(resp.status)
            logging.debug(resp.read())
        except TimeoutError:
            logging.debug('timed-out')
        finally:
            logging.debug('preceding')

    @staticmethod
    def read_sensor() -> bytes:
        if platform.system() == 'Linux':
            return os.urandom(100)
        else:
            raise NotImplementedError(f'Other platform {platform.system()}')
            # return b'12312313'

    def supervisor(self):
        print("11")
        thr_snd = Thread(target=self.sender)
        thr_ftc = Thread(target=self.fetcher)

        thr_snd.start()
        thr_ftc.start()
        print("started")
        return thr_snd, thr_ftc

    def sender(self):
        while True:
            logging.debug('calling send')
            data = self.read_sensor()
            self.send_data(data)
            time.sleep(self.sleep_time)

    def fetcher(self):
        time.sleep(.1)
        while True:
            logging.debug('calling fetch')
            self.fetch_data()
            time.sleep(self.sleep_time * 2)

    class Server(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
            self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))


if __name__ == '__main__':
    # check if env variable IP_ADDR exists and get it
    ip_addr = os.environ['IP_ADDR'] if 'IP_ADDR' in os.environ else None
    print(platform.system())
    Sensor(_target_addr=ip_addr)
