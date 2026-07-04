import sys
import urllib.request

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/healthz", timeout=3) as r:
        if r.status != 200:
            sys.exit(1)
except Exception:
    sys.exit(1)
