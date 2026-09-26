"""r281 bm-b rebase resolver #2: 16 UU/AA files (bm-a round collision).

Adjudication (hand-classified per SKILL.md, zero UNKNOWN left):
- take ours(:2=origin/bm-a, newer wall-clock) raw bytes: daily_report pair,
  scorecard_v1, strategy_scorecard, token_usage, futures/heat/lhb/update_status,
  fundamental_b_layer_filter, regime_state (only 'updated' differs),
  dashboard_status.json, dashboard_status.js (producer wrapper byte-exact).
- take theirs(:3=mine) raw bytes: daily_scorecard.json -- zero-wall-clock
  deterministic view; my side consumed the NEWEST post_review tail (00:00:16
  rows = the union ledger tail written by resolver #1; bm-a's side stopped at
  23:50:02). Same-producer pairing law (r265) + union-consistency.
- union: CODELY.md line-level (memory-union R208/r212);
  compute_audit.json rolling-ledger: history union zero-loss + latest=ours.
Byte-exact take-side from stage blobs (r270 sha discipline, no re-serialize).
"""
import json
import subprocess


def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout


def take(rev, path):
    b = blob(rev, path)
    with open(path, "wb") as f:
        f.write(b)
    return len(b)


TAKE_OURS = [
    "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/token_usage.json", "results/futures_update_status.json",
    "results/heat_update_status.json", "results/lhb_update_status.json",
    "results/update_status.json", "results/fundamental_b_layer_filter.json",
    "results/regime_state.json", "results/dashboard_status.json",
    "results/dashboard_status.js",
]
TAKE_THEIRS = ["results/daily_scorecard.json"]

for p in TAKE_OURS:
    n = take(":2", p)
    print(f"take-ours  {p} ({n}B)")
for p in TAKE_THEIRS:
    n = take(":3", p)
    print(f"take-theirs {p} ({n}B)")

# ---- compute_audit.json: rolling-ledger union + latest=ours ----
p = "results/compute_audit.json"
o = json.loads(blob(":2", p).decode("utf-8-sig"))
t = json.loads(blob(":3", p).decode("utf-8-sig"))
ho, ht = o.get("history", []), t.get("history", [])
seen, hist = set(), []
for e in ho + ht:
    k = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        hist.append(e)
merged = dict(o)
merged["history"] = hist
raw2 = blob(":2", p)
eol = "\r\n" if raw2.count(b"\r\n") > 0 else "\n"
txt = json.dumps(merged, ensure_ascii=False, indent=1)
if raw2.endswith(b"\n"):
    txt += "\n"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(txt.replace("\n", eol))
json.loads(open(p, encoding="utf-8-sig").read())
print(f"compute_audit: history {len(ho)}+{len(ht)} -> union {len(hist)} (zero-loss), latest=ours")

# ---- CODELY.md: line-level memory union ----
p = "CODELY.md"
a = blob(":2", p).decode("utf-8-sig").splitlines()
b = blob(":3", p).decode("utf-8-sig").splitlines()
seen, out = set(), []
for l in a + b:
    if l not in seen:
        seen.add(l)
        out.append(l)
raw2 = blob(":2", p)
txt = "\n".join(out) + ("\n" if raw2.endswith(b"\n") else "")
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(txt.replace("\n", "\r\n" if raw2.count(b"\r\n") > 0 else "\n"))
print(f"CODELY.md: union lines {len(a)}+{len(b)} -> {len(out)} (dedup {len(a)+len(b)-len(out)})")
