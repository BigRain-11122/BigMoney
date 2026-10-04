# -*- coding: utf-8 -*-
# r667 bm-b UU face structure probe (ASCII-only console per pit-encoding)
import json, subprocess, io, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def blob(ref, path):
    p = subprocess.run(["git", "show", ref + ":" + path], capture_output=True)
    assert p.returncode == 0, (ref, path)
    return p.stdout

faces = ["results/regime_state.json", "results/_attrition_guard_scan.json",
         "docs/daily_report/REPORT-2026-10-04.json", "docs/live_usage/LIVE-2026-10-04.json",
         "docs/live_usage/LIVE-latest.json", "results/fundamental_b_layer_filter.json",
         "results/futures_update_status.json", "results/lhb_update_status.json",
         "results/update_status.json", "results/compute_audit.json",
         "results/token_usage.json"]
for f in faces:
    o = json.loads(blob("HEAD", f).decode("utf-8", "replace"))
    t = json.loads(blob("MERGE_HEAD", f).decode("utf-8", "replace"))
    keys = sorted(o.keys())
    print("==", f)
    print("  keys:", keys[:14])
    for k in ("generated", "updated", "ts", "asof", "scan_ts", "generated_at", "now"):
        if k in o or k in t:
            print("  ts-key %r: ours=%r theirs=%r" % (k, o.get(k), t.get(k)))
    for lk in ("history", "transitions", "ledgers", "machines"):
        if lk in o:
            print("  ledger %r: ours n=%d theirs n=%d" % (lk, len(o[lk] or []), len(t.get(lk) or [])))
