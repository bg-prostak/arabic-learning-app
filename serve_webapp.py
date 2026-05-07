from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


HOST = "127.0.0.1"
PORT = 8080


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Web app: http://{HOST}:{PORT}/webapp/index.html")
    server.serve_forever()
