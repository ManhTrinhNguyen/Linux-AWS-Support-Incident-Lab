"""Check observable symptoms. Usage: python3 scripts/verify.py healthy|permissions|..."""
import argparse
import json
import urllib.error
import urllib.request

EXPECTED = {"healthy": ("GET", "/health", 200, "ok"),
            "stopped-backend": ("GET", "/", 502, None),
            "wrong-port": ("GET", "/", 502, None),
            "permissions": ("POST", "/notes", 500, "write_failed"),
            "disk-full": ("POST", "/notes", 500, "storage_full"),
            "timeout": ("GET", "/", 504, None),
            "write-ok": ("POST", "/notes", 201, "saved")}

def check(base, scenario):
    method, path, expected, marker = EXPECTED[scenario]
    req = urllib.request.Request(base + path, method=method, data=b"" if method == "POST" else None)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status, body = response.status, response.read().decode()
    except urllib.error.HTTPError as response:
        status, body = response.code, response.read().decode()
    assert status == expected, f"Expected {expected}, got {status}: {body}"
    if marker:
        result = json.loads(body)
        assert marker in result.values(), result
    print(f"PASS {scenario}: HTTP {status}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("scenario", choices=EXPECTED)
    p.add_argument("--base", default="http://127.0.0.1:8080")
    args = p.parse_args()
    check(args.base.rstrip("/"), args.scenario)
