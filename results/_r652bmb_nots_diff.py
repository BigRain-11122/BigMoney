# -*- coding: utf-8 -*-
# r652 bm-b no-ts face deep compare (LIVE/CA/TU): subprocess raw-bytes git show (r645/pit-ps law)
import json, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FACES = [
    ("LIVE", "docs/live_usage/LIVE-2026-10-04.json"),
    ("CA", "results/compute_audit.json"),
    ("TU", "results/token_usage.json"),
]

for name, path in FACES:
    p = subprocess.run(["git", "show", "origin/main:" + path], capture_output=True, timeout=30)
    o = json.loads(p.stdout.decode("utf-8"))
    m = json.load(open(path, encoding="utf-8"))
    diffs = [k for k in sorted(set(m.keys()) | set(o.keys())) if m.get(k) != o.get(k)]
    print(name, path)
    print("  differing top-level keys:", diffs[:14])
    for k in diffs[:8]:
        mv, ov = m.get(k), o.get(k)
        print("   - %s: mine=%s | origin=%s" % (k, str(mv)[:90], str(ov)[:90]))
