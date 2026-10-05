"""r756 bm-a: re-resolve the daily_report twin after the mixed-separator probe heal.

Round 1 of _r756bma_merge_resolve.py compared ts strings lexicographically;
origin's T-format data key (03:56:20+08:00) string-beat local's space-format
generated key (04:03:03) -> wrong side taken for REPORT-2026-10-06.{json,md}.
This script re-runs ONLY that twin with the healed normalized comparator and
byte-copies both twin faces from the correctly-identified side. Idempotent.
"""
import json
import re
import subprocess
from datetime import datetime

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def norm_ts(s):
    s = s.replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            d = datetime.strptime(s, fmt)
            return d.strftime("%Y%m%d%H%M%S")
        except ValueError:
            continue
    return None


def staged_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def deep_ts(obj):
    best = None

    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and TS_RE.match(x):
            n = norm_ts(x)
            if n and (best is None or n > best):
                best = n

    walk(obj)
    return best


json_path = "docs/daily_report/REPORT-2026-10-06.json"
md_path = "docs/daily_report/REPORT-2026-10-06.md"
ta = deep_ts(json.loads(staged_bytes(json_path, 2).decode("utf-8")))
tb = deep_ts(json.loads(staged_bytes(json_path, 3).decode("utf-8")))
# tie -> HEAD per r140 law; here HEAD is local (merge = local HEAD)
stage, side = (3, "local") if (tb is not None and (ta is None or tb >= ta)) else (2, "origin")
jb = staged_bytes(json_path, stage)
open(json_path, "wb").write(jb)
json.loads(open(json_path, "rb").read().decode("utf-8"))
mb = staged_bytes(md_path, stage)
open(md_path, "wb").write(mb)
print(f"re-resolved: {json_path} + md -> {side} side (origin_ts={ta} local_ts={tb})")
