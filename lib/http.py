"""Shared HTTP helpers for fetch scripts.

ICM principle: fetch scripts do one mechanical thing and write plain JSON to
disk. They never raise on a network/API error in a way that crashes the
pipeline. On failure they write a stub with an `_error` key so the stage agent
can read it, see the failure, and tag the gap `[verify]`.
"""
import json
import os
import sys
import time
from pathlib import Path
from urllib import request, parse, error

# Minimal .env loader (no dependency on python-dotenv)
def load_env():
    root = Path(__file__).resolve().parents[1]
    env = root / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

load_env()


def _request(method, url, headers=None, data=None, timeout=30):
    headers = headers or {}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    req = request.Request(url, data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url, params=None, headers=None, retries=3, backoff=1.5):
    if params:
        url = url + ("&" if "?" in url else "?") + parse.urlencode(params)
    return _with_retries("GET", url, headers, None, retries, backoff)


def post_json(url, data, headers=None, retries=3, backoff=1.5):
    return _with_retries("POST", url, headers, data, retries, backoff)


def _with_retries(method, url, headers, data, retries, backoff):
    last = None
    for attempt in range(retries):
        try:
            return _request(method, url, headers=headers, data=data)
        except error.HTTPError as e:
            # 4xx (except 429) are not worth retrying
            if e.code != 429 and 400 <= e.code < 500:
                raise
            last = e
        except (error.URLError, TimeoutError, ConnectionError) as e:
            last = e
        time.sleep(backoff ** attempt)
    raise last


def write_output(out_dir, name, payload):
    """Write payload as <out_dir>/<name>.json. Returns the path."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2))
    return path


def fail_stub(out_dir, name, message):
    """Write an error stub and exit 0 so the pipeline can continue."""
    path = write_output(out_dir, name, {"_error": message, "_source": name})
    print(f"WARNING: {name} fetch failed: {message}", file=sys.stderr)
    print(f"Wrote error stub {path}")
    sys.exit(0)


def require_key(out_dir, name, env_var):
    key = os.environ.get(env_var)
    if not key:
        fail_stub(out_dir, name,
                  f"missing API key {env_var} in .env "
                  f"(get one and add {env_var}=... to .env)")
    return key
