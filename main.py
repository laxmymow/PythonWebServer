# Http server from https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch/
import socket
import os
import mimetypes

class TCPServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host: str = host
        self.port: int = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)

        print("Listening at", s.getsockname())

        while True:
            conn, addr = s.accept()
            print("Connectedd by", addr)
            data = conn.recv(1024)

            response = self.handle_request(data)

            conn.sendall(response)
            conn.close()

    def handle_request(self, data):
        return data

class HTTPServer(TCPServer):
    headers = {
        'Server': 'WilkServer',
        'Content-Type': 'text/html'
    }

    status_codes = {
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented',
    }

    def handle_request(self, data):
        request = HTTPRequest(data)
        try:
            handler = getattr(self, f'handle_{request.method}')
        except AttributeError:
            handler = self.HTTP_501_handler

        response = handler(request)
        return response
    
    def HTTP_501_handler(self, request):
        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        blank_line = b"\r\n"
        response_body = b"<h1>501 Not Implemented</h1>"

        return b"".join([response_line, response_headers, blank_line, response_body])

    def handle_GET(self, request):
        filename = request.uri.strip('/')
        if os.path.exists(filename):
            response_line = self.response_line(status_code=200)

            content_type = mimetypes.guess_type(filename)[0] or 'text/html'
            extra_headers = {'Content-Type': content_type}
            response_headers = self.response_headers(extra_headers)

            with open(filename, 'rb') as f:
                response_body = f.read()
        else:
            response_line = self.response_line(status_code=404)
            response_headers = self.response_headers()
            response_body = b"<h1>404 Not Found</h1>"

        blank_line = b"\r\n"

        return b"".join([response_line, response_headers, blank_line, response_body])
    
    def response_line(self, status_code):
        reason = self.status_codes[status_code]
        line = f"HTTP/1.1 {status_code} {reason}\r\n"

        return line.encode()

    def response_headers(self, extra_headers=None):
        headers_copy = self.headers.copy()

        if extra_headers: headers_copy.update(extra_headers)

        headers = ""

        for h in headers_copy:
            headers += f"{h}: {headers_copy[h]}\r\n"
        
        return headers.encode()

class HTTPRequest:
    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_sersion = "1.1"

        self.parse(data)
    
    def parse(self, data):
        lines = data.split(b'\r\n')
        request_line = lines[0]
        words = request_line.split(b" ")
        self.method = words[0].decode()

        if len(words) > 1:
            self.uri = words[1].decode()
        
        if len(words) >2:
            self.http_version = words[2]

if __name__ == "__main__":
    server = HTTPServer()
    server.start()