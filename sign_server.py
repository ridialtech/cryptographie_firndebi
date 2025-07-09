import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import cgi
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVEUR_DIR = os.path.join(BASE_DIR, 'serveur')
KEY_DIR = os.path.join(BASE_DIR, 'keys')
PRIVATE_KEY = os.path.join(KEY_DIR, 'private.pem')
PUBLIC_KEY = os.path.join(KEY_DIR, 'public.pem')

os.makedirs(SERVEUR_DIR, exist_ok=True)

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_POST(self):
        if self.path != '/sign':
            self._set_headers(404)
            self.wfile.write(b'{"error": "not found"}')
            return
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                environ={'REQUEST_METHOD': 'POST',
                                         'CONTENT_TYPE': self.headers['Content-Type']})
        if 'file' not in form:
            self._set_headers(400)
            self.wfile.write(b'{"error": "file not provided"}')
            return
        file_item = form['file']
        filename = os.path.basename(file_item.filename)
        file_path = os.path.join(SERVEUR_DIR, filename)
        with open(file_path, 'wb') as f:
            f.write(file_item.file.read())
        sig_path = file_path + '.sig'
        subprocess.run(['openssl', 'dgst', '-sha256', '-sign', PRIVATE_KEY,
                        '-out', sig_path, file_path], check=True)
        self._set_headers()
        self.wfile.write(json.dumps({'message': 'signed', 'file': filename}).encode())

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != '/verify':
            self._set_headers(404)
            self.wfile.write(b'{"error": "not found"}')
            return
        params = parse_qs(parsed.query)
        filename = params.get('file', [None])[0]
        if not filename:
            self._set_headers(400)
            self.wfile.write(b'{"error": "file parameter required"}')
            return
        file_path = os.path.join(SERVEUR_DIR, filename)
        sig_path = file_path + '.sig'
        if not os.path.exists(file_path) or not os.path.exists(sig_path):
            self._set_headers(404)
            self.wfile.write(b'{"error": "file not found"}')
            return
        result = subprocess.run(['openssl', 'dgst', '-sha256', '-verify', PUBLIC_KEY,
                                 '-signature', sig_path, file_path], stdout=subprocess.PIPE)
        valid = b'Verified OK' in result.stdout
        self._set_headers()
        self.wfile.write(json.dumps({'file': filename, 'valid': valid}).encode())


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
