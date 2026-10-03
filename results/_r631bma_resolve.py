# -*- coding: utf-8 -*-
# r631 bm-a rebase UU resolver: twin snapshots take-new (local side newer by deep-ts probe),
# byte-copy same-side for md twins (r329), attrition scan manual-class=snapshot take-new.
import subprocess, json, io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# probe verdicts (deep-ts, 2026-10-03):
#   REPORT-2026-10-03.json :2:16:11:43 :3:16:25:18 -> take :3
#   LIVE-2026-10-03.json   :2:16:11:44 :3:16:25:19 -> take :3
#   fundamental_b_layer_filter.json :2:16:11:24 :3:16:25:02 -> take :3
#   _attrition_guard_scan.json      :2:16:18:36 :3:16:26:47 -> take :3 (manual class: per-run verdict snapshot R216)
TAKE_LOCAL = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/fundamental_b_layer_filter.json",
    "results/_attrition_guard_scan.json",
]

def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} read fail {path}: {r.stderr[:120]}")
    return r.stdout

ok = 0
for p in TAKE_LOCAL:
    b = stage_bytes(3, p)
    # parse-verify for json faces (r185), byte-identity is the verify for md faces
    if p.endswith(".json"):
        json.loads(b)
    with open(p, "wb") as f:
        f.write(b)
    # CR check: strip CR for size accounting only; byte-copy is verbatim
    print(f"resolved {p} <- :3: ({len(b)} bytes)")
    ok += 1

print(f"resolver done: {ok}/{len(TAKE_LOCAL)} faces")
assert ok == len(TAKE_LOCAL)
