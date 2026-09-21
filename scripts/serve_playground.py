"""Serve the playground with COOP/COEP headers required by PyScript workers."""

import functools
import http.server
import sys


class PlaygroundHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8042
    handler = functools.partial(PlaygroundHandler, directory="demoplayground")
    with http.server.HTTPServer(("", port), handler) as server:
        print(f"Serving playground at http://localhost:{port}")
        server.serve_forever()


if __name__ == "__main__":
    main()
