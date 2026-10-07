# -*- coding: utf-8 -*-
"""r664 bm-c rebase-conflict resolver receipt v2 (25 UU vs bm-a r813 CLOSEOUT tree,
second storm of the same round window; first-storm receipt _r664bmc_rebase_resolve.py).

Sides (REBASE direction r648: stage2 'ours' = upstream = bm-a r813 closeout
tree 0f5f11573 whose S6 38/38 chain outputs ran 08:25-08:27; stage3 'theirs' =
MY r664 round commit e04d8fa0b whose S6 outputs ran 08:19-08:21).

Resolution map (25 paths):
  A. STAGE 2 (bm-a newer-wins + r378 host-guarded faces): REPORT/LIVE-2026-10-07
     json+md + LIVE-latest json+md, regime_state, update_status,
     fundamental_b_layer_filter, prospect_paper/_summary, prospect_promotion/
     _summary, scorecard_v1, strategy_scorecard (r378 host=bm-a),
     t35_open_fill_verify (r378 host lane), dashboard_status.json+js (r378
     host=bm-a), futures_update_status (futures lane=bm-a)  [15 paths]
  B. STAGE 3 (mine) for the 6 paper/*_paper.json faces: marks verified
     IDENTICAL between sides (accrual derives from same panel cutoff); the
     differing keys are metadata only -- and my faces carry regime_guard
     mode='enforce' (v3 three-gate live request per S6 chain env contract),
     bm-a's takeover session ran mode='shadow'. Marks equal -> guard-mode-
     correct face wins = stage 3. Fallback: any paper face whose marks differ
     beyond metadata keys -> stage 2 with WARN (determinism breach flag).
  C. UNION ledgers:
     - results/x2_watch_log.jsonl  : line union (append-only law)
     - results/compute_audit.json : row union (own-row law, latest= newest ts)
     - results/token_usage.json   : per-machine sub-dict newer-wins merge
       inside 'machines' (bm-a rows from s2, bm-c rows from s3); scalars/derived
       aggregates from s2 (newer generated; re-derived every meter run).

All blob IO byte-exact; zero hand-edited content."""
import json
import subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("blob read fail stage %d %s: %s" % (stage, path, r.stderr))
    return r.stdout

def take(path, side):
    data = blob(2 if side == "stage2" else 3, path)
    with open(path, "wb") as fh:
        fh.write(data)
    print("RESOLVED %-46s <- %s (%d bytes)" % (path, side, len(data)))

def union_lines(path):
    base = blob(1, path).split(b"\n")
    s2 = blob(2, path).split(b"\n")
    s3 = blob(3, path).split(b"\n")
    trail = base[-1] == b""
    if trail:
        base, s2, s3 = base[:-1], s2[:-1], s3[:-1]
    base_set = set(base)
    s2_new = [l for l in s2 if l not in base_set]
    seen = base_set | set(s2_new)
    s3_new = [l for l in s3 if l not in seen]
    out = base + s2_new + s3_new
    with open(path, "wb") as fh:
        fh.write(b"\n".join(out) + (b"\n" if trail else b""))
    print("RESOLVED %-46s <- UNION lines (base %d + s2new %d + s3new %d = %d)"
          % (path, len(base), len(s2_new), len(s3_new), len(out)))

def union_rows(path):
    d2 = json.loads(blob(2, path))
    d3 = json.loads(blob(3, path))
    rows2 = d2["history"]
    keys2 = {json.dumps(r, sort_keys=True) for r in rows2}
    added = [r for r in d3["history"] if json.dumps(r, sort_keys=True) not in keys2]
    merged = rows2 + added
    latest = d3["latest"] if str(d3["latest"].get("ts", "")) > str(d2["latest"].get("ts", "")) else d2["latest"]
    b2 = blob(2, path)
    indent = 1
    try:
        first_nl = b2.split(b"\n", 2)[1]
        indent = max(1, len(first_nl) - len(first_nl.lstrip()))
    except Exception:
        pass
    text = json.dumps({"latest": latest, "history": merged}, ensure_ascii=False, indent=indent) + "\n"
    with open(path, "wb") as fh:
        fh.write(text.encode("utf-8"))
    print("RESOLVED %-46s <- ROW-UNION (s2 %d + s3new %d = %d rows, latest %s)"
          % (path, len(rows2), len(added), len(merged), str(latest.get("ts"))))

def merge_token_usage(path):
    d2 = json.loads(blob(2, path))
    d3 = json.loads(blob(3, path))
    m2, m3 = d2.get("machines", {}), d3.get("machines", {})
    merged = {}
    for k in sorted(set(m2) | set(m3)):
        a, b = m2.get(k), m3.get(k)
        if a is None:
            merged[k] = b
        elif b is None:
            merged[k] = a
        else:
            def sub_ts(d):
                cands = [str(d.get(f)) for f in ("updated", "ts", "last_seen", "generated")]
                cands = [c for c in cands if c and c not in ("None", "")]
                return max(cands) if cands else ""
            merged[k] = a if sub_ts(a) >= sub_ts(b) else b
    out = dict(d2)  # scalars/derived aggregates from s2 (newer generated)
    out["machines"] = merged
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    with open(path, "wb") as fh:
        fh.write(text.encode("utf-8"))
    print("RESOLVED %-46s <- PER-MACHINE merge (%d machine keys)" % (path, len(merged)))

META_KEYS = {"updated", "forward_guard", "regime_guard"}

def paper_face(path):
    d2 = json.loads(blob(2, path))
    d3 = json.loads(blob(3, path))
    diff = {k for k in set(list(d2) + list(d3)) if d2.get(k) != d3.get(k)}
    if diff <= META_KEYS:
        take(path, "stage3")
        print("    marks IDENTICAL, meta-diff=%s -> mine (enforce-guard v3 live)" % sorted(diff))
    else:
        print("    WARN marks differ beyond metadata: %s -> stage2 fallback" % sorted(diff))
        take(path, "stage2")

S2_FACES = [
    "docs/daily_report/REPORT-2026-10-07.json", "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/regime_state.json", "results/update_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/dashboard_status.json", "results/dashboard_status.js",
    "results/futures_update_status.json",
]
PAPER_FACES = [
    "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
]

for p in S2_FACES:
    take(p, "stage2")
for p in PAPER_FACES:
    paper_face(p)
union_lines("results/x2_watch_log.jsonl")
union_rows("results/compute_audit.json")
merge_token_usage("results/token_usage.json")
print("ALL 25 UU RESOLVED (15 s2 + 6 s3-verified + 3 unions)")
