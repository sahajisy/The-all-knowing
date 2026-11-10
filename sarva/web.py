"""A small, dependency-free web chat for Sarva (works on a phone browser).

By default it listens on 127.0.0.1 only. To use it from a phone on the same Wi-Fi, run with
``--host 0.0.0.0`` and set SARVA_PASSWORD, because anyone who can reach the page can spend
your API credits.
"""

from __future__ import annotations

import hmac
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import journal as j
from .core import Sarva

STATIC = Path(__file__).resolve().parent / "static"
PASSWORD = os.environ.get("SARVA_PASSWORD", "")
MAX_BODY = 64 * 1024

_sessions: dict[str, Sarva] = {}
_locks: dict[str, threading.Lock] = {}
_registry_lock = threading.Lock()
COMMIT = False


def _session(sid: str) -> tuple[Sarva, threading.Lock]:
    with _registry_lock:
        if sid not in _sessions:
            _sessions[sid] = Sarva()
            _locks[sid] = threading.Lock()
        return _sessions[sid], _locks[sid]


class Handler(BaseHTTPRequestHandler):
    server_version = "Sarva"

    def log_message(self, fmt, *args):  # quieter logs
        pass

    def _authorized(self) -> bool:
        if not PASSWORD:
            return True
        given = self.headers.get("X-Sarva-Password", "")
        return hmac.compare_digest(given.encode(), PASSWORD.encode())

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict | None:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return None
        try:
            data = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict) or not isinstance(data.get("sid"), str) or not 8 <= len(data["sid"]) <= 64:
            return None
        return data

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/state":
            self._json(200, {"password_required": bool(PASSWORD), "settings": j.load_settings(),
                             "library": j.library_files(), "due_reviews": len(j.due_reviews())})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if not self._authorized():
            self._json(401, {"error": "wrong password"})
            return
        data = self._body()
        if data is None:
            self._json(400, {"error": "bad request"})
            return
        sarva, lock = _session(data["sid"])
        if not lock.acquire(blocking=False):
            self._json(409, {"error": "Sarva is still answering — wait a moment."})
            return
        try:
            if self.path == "/api/chat":
                text = data.get("text")
                if not isinstance(text, str) or not text.strip():
                    self._json(400, {"error": "empty message"})
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()  # HTTP/1.0: the body streams until the connection closes
                for chunk in sarva.handle(text):
                    self.wfile.write(chunk.encode())
                    self.wfile.flush()
            elif self.path == "/api/wrap":
                self._json(200, {"text": sarva.wrap(commit=COMMIT)})
            else:
                self._json(404, {"error": "not found"})
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            lock.release()


def main(host: str = "127.0.0.1", port: int = 8765, commit: bool = False) -> None:
    global COMMIT
    COMMIT = commit
    if host not in ("127.0.0.1", "localhost") and not PASSWORD:
        suggestion = secrets.token_urlsafe(9)
        raise SystemExit(
            "Refusing to listen on a network address without a password.\n"
            f"Run e.g.:  SARVA_PASSWORD={suggestion} python -m sarva web --host {host}"
        )
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Sarva is ready → http://{host if host != '0.0.0.0' else 'localhost'}:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nまたね！")
