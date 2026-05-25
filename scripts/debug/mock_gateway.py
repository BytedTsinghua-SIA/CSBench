from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def _now() -> int:
    return int(time.time())


class Handler(BaseHTTPRequestHandler):
    server_version = "mock-gateway/0.1"

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return b""
        return self.rfile.read(length)

    def _json_response(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        body_bytes = self._read_body()
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else None
        except Exception:
            body = {"_raw": body_bytes.decode("utf-8", errors="replace")}

        record = {
            "path": self.path,
            "method": "POST",
            "headers": {k: v for k, v in self.headers.items()},
            "body": body,
            "timestamp": _now(),
        }
        print(json.dumps(record, ensure_ascii=False))
        try:
            with open("/tmp/litellm_mock_last_request.json", "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        if "chat/completions" in self.path:
            self._json_response(
                200,
                {
                    "id": "chatcmpl_mock",
                    "object": "chat.completion",
                    "created": _now(),
                    "model": "mock",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "ok"},
                            "finish_reason": "stop",
                        }
                    ],
                },
            )
            return

        if "responses" in self.path:
            self._json_response(
                200,
                {
                    "id": "resp_mock",
                    "object": "response",
                    "created_at": _now(),
                    "status": "completed",
                    "model": "mock",
                    "output": [
                        {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "ok"}],
                        }
                    ],
                    "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                },
            )
            return

        self._json_response(404, {"error": {"message": f"unknown path: {self.path}"}})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8008)
    args = parser.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"mock gateway listening on http://{args.host}:{args.port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

