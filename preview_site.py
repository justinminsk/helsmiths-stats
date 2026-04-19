from __future__ import annotations

import argparse
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_PATH = "/helsmiths-stats/"
DOCS_DIR = Path(__file__).resolve().parent / "docs"


class PagesPreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/", BASE_PATH.rstrip("/")}:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", BASE_PATH)
            self.end_headers()
            return

        super().do_GET()

    def do_HEAD(self) -> None:
        if self.path in {"/", BASE_PATH.rstrip("/")}:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", BASE_PATH)
            self.end_headers()
            return

        super().do_HEAD()

    def translate_path(self, path: str) -> str:
        if path.startswith(BASE_PATH):
            path = "/" + path[len(BASE_PATH) :]
        return super().translate_path(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preview the built GitHub Pages site locally."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    handler = partial(PagesPreviewHandler, directory=str(DOCS_DIR))
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        print(f"Serving {DOCS_DIR} at http://{args.host}:{args.port}{BASE_PATH}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping preview server.")


if __name__ == "__main__":
    main()