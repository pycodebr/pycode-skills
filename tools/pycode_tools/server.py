"""Servidor estático local (127.0.0.1) para prévia e QA."""
import contextlib
import functools
import http.server
import socketserver
import threading


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class _Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_server(directory, port=0, host="127.0.0.1"):
    handler = functools.partial(_Quiet, directory=str(directory))
    return _Server((host, port), handler)


@contextlib.contextmanager
def serve(directory, port=0):
    """with serve(pasta) as url: ...  (porta efêmera por padrão)."""
    httpd = make_server(directory, port)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
