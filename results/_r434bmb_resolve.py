# -*- coding: utf-8 -*-
# r434 bm-b: push-storm rebase conflict resolver (origin side landed 16:59-17:01 mid-my-round
# while my S6 batch committed 62b2286b2 at ~17:01). Skill: bigmoney-conflict-resolve.
# Classifier: 9 classified + 4 UNKNOWN (live_usage x4 family = same-day idempotent regen
# snapshot face per r433 manual-classification precedent, catalog gap already closed there).
# Recipes (mechanical ts probes on STAGED blobs :2:/:3:, never working tree, R350 law):
#   - compute_audit.json: rolling-ledger union (history row-identity dedup, sort ts,
#     keep newest 201 cap) + latest take-new by ts       [r188/R208/r428 cap]
#   - regime_state.json: transitions/history union + base take-new by 'updated' ts [R208]
#   - REPORT-2026-09-29 twins: take-new by generated ts, .md+.json SAME side [r98/r99]
#   - live_usage x4 (LIVE-20260929 pair + LIVE-latest pair): one regen face, all four
#     take the side chosen by LIVE-20260929.json generated ts [r433 precedent]
#   - *_status.json x3 + fundamental_b_layer_filter.json + token_usage.json: snapshot
#     take-new by updated/generated ts (deep probe, r311/r100 hardening; tie->:2: r140)
import subprocess, json, io

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout

def rowkey(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True)

def deep_ts(obj):
    """deep-scan max wall-clock ts of form 20YY-MM-DD HH:MM(:SS) (r311 probe)."""
    import re
    best = ""
    pat = re.compile(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$")
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and pat.match(v) and v > best:
                    best = v
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return best

out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
uu = [l[3:] for l in out.splitlines() if l.startswith("UU")]
print("UU files:", len(uu))
for p in uu:
    print("  ", p)

resolved, notes = [], []

# --- 1) rolling-ledger: compute_audit.json ---
p = "results/compute_audit.json"
a2 = json.loads(blob(2, p).decode("utf-8"))
a3 = json.loads(blob(3, p).decode("utf-8"))
seen, union = set(), []
for row in a2.get("history", []) + a3.get("history", []):
    k = rowkey(row)
    if k not in seen:
        seen.add(k)
        union.append(row)
union.sort(key=lambda r: str(r.get("ts", "")))
pre_trim = len(union)
union = union[-201:]  # cap semantic: keep newest 201 (r428/r433 trim precedent)
t2, t3 = str(a2.get("latest", {}).get("ts", "")), str(a3.get("latest", {}).get("ts", ""))
latest = a2["latest"] if t2 >= t3 else a3["latest"]
merged = {"latest": latest, "history": union}
with io.open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
    f.write("\n")
notes.append("compute_audit: |A|=%d |B|=%d union=%d trim->201 latest=%s (side %s)" %
             (len(a2.get("history", [])), len(a3.get("history", [])), pre_trim,
              latest.get("ts"), ":2:" if t2 >= t3 else ":3:"))
resolved.append(p)

# --- 2) rolling-ledger: regime_state.json ---
p = "results/regime_state.json"
r2 = json.loads(blob(2, p).decode("utf-8"))
r3 = json.loads(blob(3, p).decode("utf-8"))
u2, u3 = str(r2.get("updated", "")), str(r3.get("updated", ""))
base = r2 if u2 >= u3 else r3   # take-new base by updated ts (tie->:2: r140)
for key in ("transitions", "history"):
    if isinstance(base.get(key), list):
        other = (r3 if base is r2 else r2).get(key) or []
        seen, uni = set(), []
        for row in (base.get(key) or []) + other:
            k = rowkey(row)
            if k not in seen:
                seen.add(k)
                uni.append(row)
        base[key] = uni  # base order first, other-side extras appended (append-only law)
        notes.append("regime %s: |A|=%d |B|=%d union=%d (base=%s)" %
                     (key, len(base.get(key) or []), len(other), len(uni),
                      ":2:" if base is r2 else ":3:"))
with io.open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(base, f, ensure_ascii=False, indent=2)
    f.write("\n")
resolved.append(p)

# --- 3) snapshot take-new by deep ts probe: json faces (twins decided with md) ---
def snap_side(path, ts_key_hints=("generated", "generated_at", "updated", "ts")):
    o2 = json.loads(blob(2, path).decode("utf-8"))
    o3 = json.loads(blob(3, path).decode("utf-8"))
    t2, t3 = deep_ts(o2), deep_ts(o3)
    side, obj = (2, o2) if t2 >= t3 else (3, o3)   # tie->:2: (r140)
    return side, obj, t2, t3

def take_whole(side, path):
    data = blob(side, path)
    assert b"<<<<<<<" not in data, path
    with io.open(path, "wb") as f:
        f.write(data)

# REPORT-202609-29 twins: side by json generated ts; md twin forced SAME side
s, o, t2, t3 = snap_side("docs/daily_report/REPORT-2026-09-29.json")
notes.append("REPORT.json gen :2:=%s :3:=%s -> side :%d:" % (t2, t3, s))
take_whole(s, "docs/daily_report/REPORT-2026-09-29.json")
take_whole(s, "docs/daily_report/REPORT-2026-09-29.md")
resolved += ["docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"]

# live_usage x4: one regen face; side by LIVE-20260929.json generated ts; all four same side
s, o, t2, t3 = snap_side("docs/live_usage/LIVE-2026-09-29.json")
notes.append("LIVE-2026-09-29.json gen :2:=%s :3:=%s -> side :%d:" % (t2, t3, s))
for q in ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"):
    take_whole(s, q)
    resolved.append(q)

# plain snapshots: futures/lhb/update_status, fundamental filter, token_usage
for p in ("results/futures_update_status.json", "results/lhb_update_status.json",
          "results/update_status.json", "results/fundamental_b_layer_filter.json",
          "results/token_usage.json"):
    s, o, t2, t3 = snap_side(p)
    take_whole(s, p)
    resolved.append(p)
    notes.append("%s :2:=%s :3:=%s -> :%d:" % (p, t2 or "(none)", t3 or "(none)", s))

# --- verify: no markers, json parse, zero-loss ---
for p in resolved:
    raw = open(p, "rb").read()
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, "markers in " + p
    if p.endswith(".json"):
        json.loads(raw.decode("utf-8"))
missing = [p for p in uu if p not in resolved]
assert not missing, "unresolved: %s" % missing
print("resolved:", len(resolved), "of", len(uu))
for n in notes:
    print("  ", n)
