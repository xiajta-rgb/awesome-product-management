#!/usr/bin/env python3
"""
FashionSelector Pro - HTTP Server
Provides frontend dashboard and skill result API with date-based filtering
"""

import http.server
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs


class FashionSelectorHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for FashionSelector dashboard"""

    OUTPUT_DIR = "/workspace/output"

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/skill-result':
            self._serve_skill_result(parsed)
        elif parsed.path == '/api/available-dates':
            self._serve_available_dates()
        else:
            super().do_GET()

    def _serve_skill_result(self, parsed):
        params = parse_qs(parsed.query)
        date_filter = params.get('date', [None])[0]

        if date_filter:
            target_file = os.path.join(self.OUTPUT_DIR, f"skill_result_{date_filter}.json")
        else:
            target_file = os.path.join(self.OUTPUT_DIR, "skill_result.json")

        try:
            if not os.path.exists(target_file):
                self._send_error(404, f"No data found for date: {date_filter or 'latest'}")
                return

            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self._send_error(500, f"Error loading skill result: {str(e)}")

    def _serve_available_dates(self):
        try:
            dates = []
            if os.path.exists(self.OUTPUT_DIR):
                for fname in os.listdir(self.OUTPUT_DIR):
                    m = re.match(r'skill_result_(\d{4}-\d{2}-\d{2})\.json', fname)
                    if m:
                        dates.append(m.group(1))
                if os.path.exists(os.path.join(self.OUTPUT_DIR, "skill_result.json")):
                    with open(os.path.join(self.OUTPUT_DIR, "skill_result.json"), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        run_time = data.get("run_time", "")
                        if run_time:
                            try:
                                dt = datetime.fromisoformat(run_time.replace("Z", "+00:00"))
                                today_str = dt.strftime("%Y-%m-%d")
                                if today_str not in dates:
                                    dates.append(today_str)
                            except Exception:
                                pass
            dates.sort(reverse=True)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"dates": dates}, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self._send_error(500, f"Error listing dates: {str(e)}")

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
    print(f"  API: http://localhost:{port}/api/skill-result?date=YYYY-MM-DD")
    print(f"  Dates: http://localhost:{port}/api/available-dates")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*60}\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
