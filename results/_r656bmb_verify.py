# -*- coding: utf-8 -*-
# r656 verify: staged stage-0 blobs of all 21 resolved faces -- conflict-marker
# content check (r644 law) + json/jsonl parse-verify (jsonl = per-line).
import io
import json
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CREATE = 0x08000000
FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/post_review.jsonl",
    "results/post_review/REPORT-20261004.md",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
bad = 0
for f in FACES:
    p = subprocess.run(["git", "show", ":0:" + f], capture_output=True,
                        creationflags=CREATE)
    if p.returncode != 0:
        print("STAGE0-MISS", f)
        bad += 1
        continue
    raw = p.stdout
    if b"<<<<<<<" in raw or b">>>>>>>" in raw:
        print("MARKER", f)
        bad += 1
        continue
    if f.endswith(".json"):
        try:
            json.loads(raw)
        except Exception as e:
            print("PARSE-FAIL", f, repr(e)[:100])
            bad += 1
    elif f.endswith(".jsonl"):
        n = 0
        for ln in raw.decode("utf-8", "replace").splitlines():
            if not ln.strip():
                continue
            n += 1
            try:
                json.loads(ln)
            except Exception as e:
                print("LINE-FAIL", f, repr(e)[:80])
                bad += 1
                break
        print("jsonl-ok", f, "lines=", n)
print("verify:", "PASS 21/21" if bad == 0 else "BAD=%d" % bad)
sys.exit(1 if bad else 0)
