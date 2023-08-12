import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(level=logging.INFO, format='[HP][%(asctime)s][%(levelname)s] %(message)s')


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            logging.info('Request received')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><head><title>My Server</title></head>')
            self.wfile.write(b'<body><h1>Welcome to my server!</h1></body></html>')
        else:
            self.send_error(404)


def run(server_class=HTTPServer, handler_class=Server, *, port=80, address=''):
    server_address = (address, port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run(address='10.0.0.100')
