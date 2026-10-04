# -*- coding: utf-8 -*-
"""r684 bm-a merge UU resolver (16 faces). Routing per r683 canon, directions
derived per-face (r461 ts law, no assumption):
- 12 S6 regen snapshot faces = whole-face ts-freshness (ours 15:44-47 vs
  theirs ~15:38-41 -- expected OURS-newer this round; resolver decides per
  face by max ts, r440 regen-family law);
- token_usage.json = r456/r679 per-key machines union (side_pick>0 asserted,
  r466 whole-face freshness fallback if zero);
- pool_core_samples.jsonl = line-set zero-loss UNION (this round git left it
  UU, not auto-merged: union = HEAD lines + MERGE_HEAD-unique lines appended,
  r675 block-append law; containment proof both directions, r656 family);
- runnable_pool.json = THEIRS (origin-newer: bm-b 565e5b0b4 CRLF face + w3
  claims; our committed side = daemon-synced stale intermediate with zero
  bm-a-unique bytes) + post-claim intact assertions.
Writes winner bytes verbatim via subprocess git show (zero PS pipe, r660 law)."""
import json
import subprocess
import sys

WHOLE_FACE = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
TWIN_OF = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
TOKEN = "results/token_usage.json"
POOL_SAMPLES = "results/pool_core_samples.jsonl"
POOL = "results/runnable_pool.json"
report = []


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    assert r.returncode == 0, f"git show {ref}:{path} rc={r.returncode} {r.stderr[:200]!r}"
    return r.stdout


def ts_norm(v):
    if v is None:
        return ""
    s = str(v)
    if len(s) < 10 or s[4] != "-" or s[7] != "-":
        return ""
    return s.replace("T", " ")[:19]


def entry_ts(ent):
    if not isinstance(ent, dict):
        return ""
    best = ""
    for k, v in ent.items():
        if isinstance(v, (str, int)) and any(t in k.lower() for t in
                ("ts", "updated", "generated", "time")):
            n = ts_norm(v)
            if n > best:
                best = n
    return best


def _flat_ts(obj):
    vals = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, int)) and any(t in k.lower() for t in
                    ("ts", "updated", "generated", "asof", "clock", "time")):
                vals.append(v)
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, (str, int)) and any(t in k2.lower() for t in
                            ("ts", "updated", "generated", "time")):
                        vals.append(v2)
    return vals


decision = {}
for p in WHOLE_FACE:
    ours = show("HEAD", p)
    theirs = show("MERGE_HEAD", p)
    do, dt = json.loads(ours), json.loads(theirs)
    o_ts = max(ts_norm(v) for v in _flat_ts(do))
    t_ts = max(ts_norm(v) for v in _flat_ts(dt)) if _flat_ts(dt) else ""
    take_theirs = t_ts >= o_ts
    decision[p] = take_theirs
    with open(p, "wb") as f:
        f.write(theirs if take_theirs else ours)
    report.append(f"{p}: ours {o_ts} vs theirs {t_ts} -> {'THEIRS' if take_theirs else 'OURS'}")
for p, twin in TWIN_OF.items():
    take_theirs = decision[twin]
    with open(p, "wb") as f:
        f.write(show("MERGE_HEAD", p) if take_theirs else show("HEAD", p))
    report.append(f"{p}: follows json twin -> {'THEIRS' if take_theirs else 'OURS'}")

# ---- token_usage.json: r456/r679 per-key machines union ----
ours = json.loads(show("HEAD", TOKEN))
theirs = json.loads(show("MERGE_HEAD", TOKEN))
mo, mt = ours.get("machines", {}), theirs.get("machines", {})
union = {}
picks = {"ours": 0, "theirs": 0, "equal": 0}
for k in sorted(set(mo) | set(mt)):
    a, b = mo.get(k), mt.get(k)
    if k not in mo:
        union[k] = b; picks["theirs"] += 1; continue
    if k not in mt:
        union[k] = a; picks["ours"] += 1; continue
    ta, tb = entry_ts(a), entry_ts(b)
    if ta > tb:
        union[k] = a; picks["ours"] += 1
    elif tb > ta:
        union[k] = b; picks["theirs"] += 1
    else:
        union[k] = a; picks["equal"] += 1
if picks["ours"] + picks["theirs"] == 0:
    o_g, t_g = ts_norm(ours.get("generated")), ts_norm(theirs.get("generated"))
    winner, wref = (ours, "HEAD") if o_g >= t_g else (theirs, "MERGE_HEAD")
    with open(TOKEN, "wb") as f:
        f.write(show(wref, TOKEN))
    report.append(f"{TOKEN}: r466 whole-face fallback {wref} (side_pick=0, picks={picks})")
else:
    base = ours if ts_norm(ours.get("generated")) >= ts_norm(theirs.get("generated")) else theirs
    merged = dict(base)
    merged["machines"] = union
    with open(TOKEN, "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    report.append(f"{TOKEN}: per-key machines union picks={picks} top-level={'ours' if base is ours else 'theirs'} ({base.get('generated')})")

# ---- pool_core_samples.jsonl: line-level zero-loss UNION (UU this round) ----
h_raw = show("HEAD", POOL_SAMPLES).decode("utf-8", "replace")
m_raw = show("MERGE_HEAD", POOL_SAMPLES).decode("utf-8", "replace")
h_lines = h_raw.splitlines()
m_lines = m_raw.splitlines()
h_set, m_set = set(h_lines), set(m_lines)
appended = [ln for ln in m_lines if ln not in h_set]
merged_text = "\n".join(h_lines + appended) + ("\n" if (h_raw.endswith("\n") or m_raw.endswith("\n")) else "")
with open(POOL_SAMPLES, "w", encoding="utf-8", newline="") as f:
    f.write(merged_text)
final_set = set(merged_text.splitlines())
missing_h = h_set - final_set
missing_m = m_set - final_set
assert not missing_h and not missing_m, f"zero-loss FAIL: head-missing={len(missing_h)} merge-missing={len(missing_m)}"
report.append(f"{POOL_SAMPLES}: zero-loss union PASS (head={len(h_set)} mergehead={len(m_set)} merged={len(final_set)} appended_theirs={len(appended)})")

# ---- runnable_pool.json: THEIRS (origin-newer) + claim intact assertions ----
theirs_pool = show("MERGE_HEAD", POOL)
with open(POOL, "wb") as f:
    f.write(theirs_pool)
d = json.loads(theirs_pool)
w3 = [e for e in d.get("entries", []) if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD")]
claimed = [(s.get("key"), s.get("owner"), s.get("owner_since"))
           for e in w3 for s in (e.get("shards") or []) if s.get("owner")]
report.append(f"{POOL}: THEIRS origin-newer (updated_at={d.get('updated_at')}); W3 entries={len(w3)} claimed-shards={claimed}")
assert len(w3) == 4, f"expected 4 W3 screen shards, got {len(w3)}"
assert any(o == "bm-c" and os_ == "2026-10-04 15:41:38" for _, o, os_ in claimed), \
    f"expected bm-c SHARD-0 claim 15:41:38 (cdf8729cf) in entries[].shards[] (r675bm-b law), got {claimed}"

print("\n".join(report))
print("RESOLVED 16 UU faces (12 regen ts-freshness + token per-key union + pool_samples zero-loss union + pool theirs)")
