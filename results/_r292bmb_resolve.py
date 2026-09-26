# -*- coding: utf-8 -*-
"""r292 bm-b rebase-resolve: 16 UU per bigmoney-conflict-resolve canonical recipes.

Sides in rebase: stage2(ours)=upstream bm-a face, stage3(theirs)=bm-b r292 face.
Recipes:
- memory-union CODELY.md       : HEAD(bm-a) full face + bm-b new tail lines appended (line union, dedupe)
- rolling-ledger compute_audit  : history union zero-loss + latest take-new-by-ts (bm-b)
- rolling-ledger regime_state   : history/transitions union + state take-new (bm-b)
- js-wrapper dashboard_status.js: whole-byte take-side by generated_at (bm-b 03:23:45 > 03:20:15)
- snapshot (x7 + report twins + scorecards): take-new by ts (all bm-b newer this window)
Consumer faces get re-derived post-merge anyway (daily_scorecard/strategy_scorecard/
daily_report/build_status rerun in addendum commit) -- take-side here is provisional.
"""
import json
import subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail %s %s" % (stage, path))
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def write(path, data, raw=None):
    if raw is not None:
        open(path, "wb").write(raw)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

resolved = []

# ---------- 1) CODELY.md: memory-union ----------
ours = blob(2, "CODELY.md").decode("utf-8")
theirs = blob(3, "CODELY.md").decode("utf-8")
ours_lines = ours.splitlines()
theirs_lines = theirs.splitlines()
# bm-b new lines = in theirs tail but not in ours face (line-level, dedupe identical)
ours_set = set(ours_lines)
bmb_new = [l for l in theirs_lines if l not in ours_set and l.strip()]
# sanity: expect exactly 1 new bm-b line (r292 footer kenglu)
assert len(bmb_new) == 1, "expected 1 new bm-b CODELY line, got %d: %r" % (len(bmb_new), bmb_new)
merged = ours.rstrip("\n") + "\n" + "\n".join(bmb_new) + "\n"
open("CODELY.md", "w", encoding="utf-8", newline="\n").write(merged)
assert "bm-a R290" in merged and "bm-b R292" in merged
assert "<<<<<<<" not in merged and "=======" not in merged and ">>>>>>>" not in merged
resolved.append(("CODELY.md", "memory-union: bm-a face + bm-b r292 line (+%d)" % len(bmb_new)))

# ---------- 2) compute_audit.json: history union + latest take-new ----------
o, t = jload(blob(2, "results/compute_audit.json")), jload(blob(3, "results/compute_audit.json"))
oh = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in o.get("history", [])}
th = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in t.get("history", [])}
union = list({**oh, **th}.values())
union.sort(key=lambda r: str(r.get("ts", "")))
merged = dict(t)  # theirs = bm-b newest latest face
merged["history"] = union
n_o, n_t = len(o.get("history", [])), len(t.get("history", []))
assert len(union) >= max(n_o, n_t), "union lost rows"
write("results/compute_audit.json", merged)
resolved.append(("results/compute_audit.json", "history union %d|%d->%d + latest bm-b" % (n_o, n_t, len(union))))

# ---------- 3) regime_state.json: history union + state take-new ----------
o, t = jload(blob(2, "results/regime_state.json")), jload(blob(3, "results/regime_state.json"))
merged = dict(t)
for key in ("history", "transitions"):
    if key in o or key in t:
        ol = o.get(key, []); tl = t.get(key, [])
        um = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in ol}
        for r in tl:
            um.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged[key] = list(um.values())
write("results/regime_state.json", merged)
resolved.append(("results/regime_state.json", "history union + state take-new bm-b"))

# ---------- 4) token_usage.json: history-if-present union else take-new ----------
o, t = jload(blob(2, "results/token_usage.json")), jload(blob(3, "results/token_usage.json"))
if isinstance(o.get("history"), list) and isinstance(t.get("history"), list):
    um = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in o["history"]}
    for r in t["history"]:
        um.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
    merged = dict(t); merged["history"] = list(um.values())
    write("results/token_usage.json", merged)
    resolved.append(("results/token_usage.json", "history union + take-new"))
else:
    write("results/token_usage.json", t)
    resolved.append(("results/token_usage.json", "snapshot take-new bm-b"))

# ---------- 5) js-wrapper + json twin + snapshot family: whole take-side (bm-b newer all) ----------
snap = {
    "results/dashboard_status.js": "raw",      # whole bytes, producer wrapper preserved
    "results/dashboard_status.json": "json",
    "results/fundamental_b_layer_filter.json": "json",
    "results/futures_update_status.json": "json",
    "results/heat_update_status.json": "json",
    "results/lhb_update_status.json": "json",
    "results/update_status.json": "json",
    "docs/daily_report/REPORT-2026-09-27.json": "json",
    "docs/daily_report/REPORT-2026-09-27.md": "raw",
    "results/daily_scorecard.json": "json",
    "results/scorecard_v1.json": "json",
    "results/strategy_scorecard.json": "json",
}
for path, kind in snap.items():
    raw = blob(3, path)  # theirs = bm-b, newer ts on every probed face this window
    if kind == "raw":
        open(path, "wb").write(raw)
    else:
        d = jload(raw)          # parse gate (r185) before write
        write(path, d)
    resolved.append((path, "take-side bm-b (newer ts; consumer faces re-derived post-merge)"))

# ---------- parse gate over every resolved json ----------
for path, kind in snap.items():
    if kind == "json":
        json.loads(open(path, encoding="utf-8-sig").read())
json.loads(open("results/compute_audit.json", encoding="utf-8-sig").read())
json.loads(open("results/regime_state.json", encoding="utf-8-sig").read())
json.loads(open("results/token_usage.json", encoding="utf-8-sig").read())

for p, note in resolved:
    print("RESOLVED", p, "--", note)
print("OK: %d files resolved, parse gates green" % len(resolved))
