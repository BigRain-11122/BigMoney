# -*- coding: utf-8 -*-
"""r316 bm-b push-collision resolver (14 UU batch, classify_conflicts recipes).
ours(stage2)=origin side (bm-c r74b S6 @10:28-10:30 + bm-a r312 drain), theirs(stage3)=my r316 replay (S6 @10:35-10:38, newer).
Recipes: compute_audit=rolling-ledger history union (zero row loss) + latest take-new; all others=my side is newer on every
internal ts -> take-side whole bytes (stage3). Per r140 same-second tie -> HEAD; here mine strictly newer on all ts faces.
"""
import subprocess, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def blob(stage, path):
    b = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout
    if not b:
        raise RuntimeError(f"empty blob stage{stage} {path}")
    return b

# 1) rolling-ledger: results/compute_audit.json -- union history by ts, latest take-new
p = "results/compute_audit.json"
j2, j3 = json.loads(blob(2, p)), json.loads(blob(3, p))
h2, h3 = j2["history"], j3["history"]
by_ts2 = {r["ts"]: r for r in h2}
by_ts3 = {r["ts"]: r for r in h3}
union_ts = sorted(set(by_ts2) | set(by_ts3))
union = [by_ts3.get(t) or by_ts2[t] for t in union_ts]
assert len(union) == len(set(by_ts2) | set(by_ts3)), "union line-count law failed"
merged = dict(j3)  # mine is the newer envelope (latest ts 10:35:39 vs 10:28:09)
merged["history"] = union
merged["latest"] = j3["latest"] if j3["latest"]["ts"] >= j2["latest"]["ts"] else j2["latest"]
b2raw = blob(2, p)
indent = len(re.search(rb'\n(\s+)"', b2raw).group(1))
crlf = b"\r\n" in b2raw
out = json.dumps(merged, ensure_ascii=False, indent=indent)
if crlf:
    out = out.replace("\n", "\r\n")
(ROOT / p).write_bytes(out.encode("utf-8") + (b"\r\n" if crlf else b"\n"))
json.loads((ROOT / p).read_text(encoding="utf-8"))
print(f"[union] {p}: history {len(h2)}|{len(h3)} -> {len(union)} rows (|A u B| law PASS), latest ts {merged['latest']['ts']}, indent={indent} crlf={crlf}")

# 2) take-mine whole bytes (all strictly newer on internal ts faces)
TAKE_MINE = [
    "results/regime_state.json",            # updated 10:35:42 vs 10:28:19, history equal-len
    "results/dashboard_status.json",        # same producer run as .js, mine newer
    "results/dashboard_status.js",          # js-wrapper: take-side whole bytes (R209)
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/scorecard_v1.json",            # UNKNOWN classified: deterministic re-derive, only 'generated' drifts -> take-new (mine 10:35:44)
    "results/strategy_scorecard.json",      # UNKNOWN classified: generated+audit(ts-embedded) drift -> take-new (mine 10:35:55)
    "docs/daily_report/REPORT-2026-09-27.json",  # UNKNOWN classified: rd diagnostics snapshot, mine newer (audit_latest 10:35:39)
    "docs/daily_report/REPORT-2026-09-27.md",     # same producer run as .json -> same side
]
for p in TAKE_MINE:
    b3 = blob(3, p)
    (ROOT / p).write_bytes(b3)
    if p.endswith(".json"):
        json.loads((ROOT / p).read_text(encoding="utf-8"))  # r185 law: parse-verify before add
    print(f"[take-mine] {p}: {len(b3)}B")

# 3) stage resolved files
files = ["results/compute_audit.json"] + TAKE_MINE
subprocess.run(["git", "add", "--"] + files, check=True, cwd=ROOT)
left = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, cwd=ROOT).stdout.decode()
assert not left.strip(), f"unresolved left: {left}"
print("RESOLVER OK: 14/14 staged, zero unresolved")
