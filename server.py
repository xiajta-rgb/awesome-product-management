#!/usr/bin/env python3
"""
FashionSelector Pro - HTTP Server
Provides frontend dashboard and skill result API
"""

import http.server
import json
import os
import sys
from pathlib import Path

class FashionSelectorHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for FashionSelector dashboard"""

    SKILL_RESULT_PATH = "/workspace/output/skill_result.json"

    def do_GET(self):
        if self.path == '/api/skill-result':
            self._serve_skill_result()
        else:
            super().do_GET()

    def _serve_skill_result(self):
        """Serve the latest skill result as JSON"""
        try:
            if not os.path.exists(self.SKILL_RESULT_PATH):
                self._send_error(404, "No skill result found. Please run the skill first.")
                return

            with open(self.SKILL_RESULT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self._send_error(500, f"Error loading skill result: {str(e)}")

    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        sys.stderr.write(f"[Dashboard] {format % args}\n")


def main():
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    os.chdir(frontend_dir)

    port = 8899
    server = http.server.HTTPServer(("", port), FashionSelectorHandler)

    print(f"\n{'='*60}")
    print(f"  FashionSelector Pro Dashboard")
    print(f"  http://localhost:{port}")
    print(f"  API: http://localhost:{port}/api/skill-result")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*60}\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
