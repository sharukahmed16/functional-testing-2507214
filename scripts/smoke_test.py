"""Smoke test for the live site. Uses only the Python standard library.

Environment variables
  LIVE_URL      base URL of the deployed site, e.g. https://my-app.onrender.com
  EXPECTED_SHA  commit SHA that must be live before the checks start
  WAIT_SECONDS  how long to wait for the new SHA (default 600)

Step 1 waits until /health reports EXPECTED_SHA. Then it makes three live requests:
  1. GET  /health    -> status ok and the expected SHA
  2. GET  /          -> the frontend page
  3. POST /api/call  -> divide(10, 4) returns 2.5
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

LIVE_URL = os.environ.get("LIVE_URL", "").rstrip("/")
EXPECTED_SHA = os.environ.get("EXPECTED_SHA", "").strip()
WAIT_SECONDS = int(os.environ.get("WAIT_SECONDS", "600"))
POLL_SECONDS = 10


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def request(path, payload=None):
    data = None
    headers = {"User-Agent": "smoke-test"}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(LIVE_URL + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.status, response.read().decode()


def wait_for_sha():
    deadline = time.time() + WAIT_SECONDS
    seen = None
    while time.time() < deadline:
        try:
            _, body = request("/health")
            seen = json.loads(body).get("sha")
        except (urllib.error.URLError, ValueError, OSError) as error:
            seen = f"unreachable ({error})"
        if seen == EXPECTED_SHA:
            print(f"Live site is running {EXPECTED_SHA}")
            return
        print(f"Waiting for {EXPECTED_SHA[:7]}, live site reports {seen}")
        time.sleep(POLL_SECONDS)
    fail(f"timed out after {WAIT_SECONDS}s, live SHA was {seen}")


def main():
    if not LIVE_URL or not EXPECTED_SHA:
        fail("LIVE_URL and EXPECTED_SHA must be set")

    wait_for_sha()

    status, body = request("/health")
    health = json.loads(body)
    if status != 200 or health.get("status") != "ok" or health.get("sha") != EXPECTED_SHA:
        fail(f"/health returned {status} {body}")
    print("1/3 GET /health ok")

    status, body = request("/")
    if status != 200 or "target.py test bench" not in body:
        fail(f"GET / returned {status} without the expected page")
    print("2/3 GET / ok")

    status, body = request("/api/call", {"function": "divide", "inputs": ["10", "4"]})
    result = json.loads(body)
    if status != 200 or result.get("ok") is not True or result.get("result") != "2.5":
        fail(f"POST /api/call returned {status} {body}")
    print("3/3 POST /api/call ok")

    print("Smoke test passed")


if __name__ == "__main__":
    main()
