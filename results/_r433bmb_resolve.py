# -*- coding: utf-8 -*-
# r433 bm-b: push-storm rebase conflict resolver (bm-a round landed 16:38-16:40 mid-my-round)
# Skill: bigmoney-conflict-resolve. Classifier: 14 classified + 4 UNKNOWN (live_usage family,
# manually classified = same-day idempotent regen snapshot face, catalog gap closed this round).
# Probe facts (staged blobs :2:/:3:): :2: (bm-a side) uniformly fresher by 1-4 min on every
# snapshot face (16:38-16:41 vs my 16:35-16:38); zero ties. Recipes:
#   - compute_audit.json: rolling-ledger union (history row-identity dedup, sort ts, keep newest 201)
#     + latest take-new (:2: 16:38:37 > :3: 16:35:12)     [r188/R208]
#   - regime_state.json: transitions+history union + state fields take-new (:2:)  [R208]
#   - all others incl. live_usage x4 + .md twins + dashboard_status.js: take :2: whole bytes
#     (js-wrapper law R209: whole-byte take-side, never re-emit; .md/.json twins same side r98/r99)
import subprocess, json, io, os

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout

def rowkey(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True)

out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
uu = [l[3:] for l in out.splitlines() if l.startswith("UU")]
print("UU files:", len(uu))

resolved, ledger_notes = [], []

# --- 1) rolling-ledger: compute_audit.json ---
p = "results/compute_audit.json"
a2 = json.loads(blob(2, p).decode("utf-8"))
a3 = json.loads(blob(3, p).decode("utf-8"))
seen, union = set(), []
for row in a2["history"] + a3["history"]:
    k = rowkey(row)
    if k not in seen:
        seen.add(k)
        union.append(row)
union.sort(key=lambda r: str(r.get("ts", "")))
pre_trim = len(union)
union = union[-201:]  # cap semantic: keep newest 201 (r428 trim precedent)
latest = a2["latest"] if str(a2["latest"].get("ts", "")) >= str(a3["latest"].get("ts", "")) else a3["latest"]
merged = {"latest": latest, "history": union}
with io.open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
    f.write("\n")
ledger_notes.append("compute_audit: |A|=%d |B|=%d union=%d trim->201 latest=%s" %
                   (len(a2["history"]), len(a3["history"]), pre_trim, latest.get("ts")))
resolved.append(p)

# --- 2) rolling-ledger: regime_state.json ---
p = "results/regime_state.json"
r2 = json.loads(blob(2, p).decode("utf-8"))
r3 = json.loads(blob(3, p).decode("utf-8"))
assert str(r2.get("updated", "")) >= str(r3.get("updated", "")), "regime :3: newer -- probe flip"
for key in ("transitions", "history"):
    if isinstance(r2.get(key), list):
        seen, union = set(), []
        for row in (r2.get(key) or []) + (r3.get(key) or []):
            k = rowkey(row)
            if k not in seen:
                seen.add(k)
                union.append(row)
        # stable order: keep r2 order first then r3-only extras appended (append-only ledger)
        r2[key] = union
        ledger_notes.append("regime %s: |A|=%d |B|=%d union=%d" %
                           (key, len(r2.get(key) or []), len(r3.get(key) or []), len(union)))
with io.open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(r2, f, ensure_ascii=False, indent=2)
    f.write("\n")
resolved.append(p)

# --- 3) whole-byte take :2: for everything else ---
for p in uu:
    if p in resolved:
        continue
    data = blob(2, p)
    assert b"<<<<<<<" not in data, p
    with io.open(p, "wb") as f:
        f.write(data)
    resolved.append(p)

# --- verify: json parse (except .js/.md), wrapper present, no markers ---
for p in resolved:
    raw = open(p, "rb").read()
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, "markers in " + p
    if p.endswith(".json"):
        json.loads(raw.decode("utf-8"))
    if p == "results/dashboard_status.js":
        assert b"window.DASH_DATA" in raw, "js wrapper stripped"
print("resolved:", len(resolved), "of", len(uu))
for n in ledger_notes:
    print("  ", n)
for p in ("docs/daily_report/REPORT-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.json",
          "results/strategy_scorecard.json", "results/update_status.json"):
    o = json.loads(open(p, "rb").read().decode("utf-8"))
    gen = o.get("generated") or o.get("generated_at") or o.get("updated") or o.get("meta", {}).get("generated_at")
    print("  side-check", p, "->", gen)
