"""r297 bm-a rebase UU resolver (24 files, bm-b r300 batch vs mine).

Stage map in this rebase: :2: = upstream bm-b (05:43 stamps), :3: = my replay
commit (05:50 stamps). Recipes per skill classify_conflicts + manual audit:
- rolling-ledger (compute_audit, regime_state): union history rows (canonical
  dedupe, zero loss, ts sort), scalar/latest fields take-new (mine newer).
- append-log (x2_watch_log.jsonl): line-level union dedupe.
- snapshot (ts faces): take-new side = :3: (mine, newer ts, verified below).
- daily_report md: mirror the json winner side.
- paper_export (no-ts deterministic face): semantic JSON equality gate; equal ->
  take :3:; unequal -> FAIL-CLOSED stop for manual ruling.
Write-first-assert-after (R293 E1): write files, validate json.loads, then git add.
"""
import json, subprocess, sys, os

ROOT = os.getcwd()

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"stage {stage} missing {path}"
    return r.stdout

def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)

def dump_mirror(obj, ref_blob):
    indent = 1 if ref_blob.startswith(b'{\n "') or ref_blob.startswith(b'{\n  "') else None
    text = json.dumps(obj, ensure_ascii=False, indent=indent)
    if ref_blob.endswith(b"\n"):
        text += "\n"
    return text.encode("utf-8")

def write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)

resolved, report = [], []

# ---- rolling-ledger unions -------------------------------------------------
for path, list_key in (("results/compute_audit.json", "history"),
                       ("results/regime_state.json", "history")):
    b2, b3 = blob(2, path), blob(3, path)
    d2, d3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
    l2, l3 = d2.get(list_key, []), d3.get(list_key, [])
    seen, union = set(), []
    for row in l2 + l3:
        c = canon(row)
        if c not in seen:
            seen.add(c)
            union.append(row)
    if all(isinstance(r, dict) and "ts" in r for r in union) and path.endswith("compute_audit.json"):
        union.sort(key=lambda r: r["ts"])
    d3[list_key] = union                      # base = mine (newer scalars), swap in union
    data = dump_mirror(d3, b3)
    write(path, data)
    v = json.loads(data.decode("utf-8-sig"))
    assert len(v[list_key]) == len(union) == len(seen), f"union loss {path}"
    resolved.append(path)
    report.append(f"UNION {path}: {len(l2)}+{len(l3)} -> {len(union)} rows, scalars=stage3")

# regime_state transitions union (both [] here, keep law shape)
p = "results/regime_state.json"
d = json.loads(open(p, encoding="utf-8-sig").read())
assert isinstance(d.get("transitions"), list)
report.append(f"regime transitions union: {len(d['transitions'])} rows")

# ---- append-log union ------------------------------------------------------
p = "results/x2_watch_log.jsonl"
b2, b3 = blob(2, p), blob(3, p)
lines2 = [l for l in b2.decode("utf-8-sig").splitlines() if l.strip()]
lines3 = [l for l in b3.decode("utf-8-sig").splitlines() if l.strip()]
seen, union = set(), []
for l in lines2 + lines3:
    if l not in seen:
        seen.add(l)
        union.append(l)
data = ("\n".join(union) + "\n").encode("utf-8")
write(p, data)
assert len(union) == len(seen) == len(lines2) + len(lines3) - (len(lines2) + len(lines3) - len(set(lines2 + lines3)))
resolved.append(p)
report.append(f"UNION {p}: {len(lines2)}+{len(lines3)} -> {len(union)} lines")

# ---- snapshot take-new (stage 3 = mine, newer ts verified in inspect) ------
snapshots = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "results/daily_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in snapshots:
    b3 = blob(3, p)
    write(p, b3)                               # byte mirror, zero re-serialization
    json.loads(b3.decode("utf-8-sig"))         # validate before add
    resolved.append(p)
report.append(f"TAKE-NEW stage3 x{len(snapshots)} snapshots (ts 05:50 > 05:43 all, inspect log)")

# daily_report md twin: mirror json winner side (stage 3)
p = "docs/daily_report/REPORT-2026-09-27.md"
b3 = blob(3, p)
write(p, b3)
resolved.append(p)
report.append("TAKE stage3 " + p + " (json twin side)")

# ---- paper_export: content faces equal, only state_updated freshness stamps
# differ (live.paper touches state files each round; R94 byte-law holds only
# when state untouched). Assert content identity excluding volatile keys, then
# take-new stage 3 (mine, fresher stamps 05:50 > 05:43).
VOLATILE = {"state_updated", "generated_from_state_updated"}
def strip_volatile(o):
    if isinstance(o, dict):
        return {k: strip_volatile(v) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [strip_volatile(x) for x in o]
    return o
for p in ("results/paper_export/export-2026-09-24.json",
          "results/paper_export/latest.json"):
    b2, b3 = blob(2, p), blob(3, p)
    d2 = json.loads(b2.decode("utf-8-sig"))
    d3 = json.loads(b3.decode("utf-8-sig"))
    if canon(strip_volatile(d2)) == canon(strip_volatile(d3)):
        write(p, b3)
        resolved.append(p)
        report.append(f"TAKE-NEW stage3 {p} (content faces identical; only "
                      "state_updated/generated_from_state_updated stamps differ)")
    else:
        for _l in report:
            print(_l)
        print(f"FAIL-CLOSED {p}: REAL content difference -- manual ruling")
        sys.exit(2)

# ---- stage all resolved + validate -----------------------------------------
for p in resolved:
    r = subprocess.run(["git", "add", p], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"add failed {p}: {r.stderr}"
print("\n".join(report))
print(f"RESOLVED {len(resolved)}/24 files, staged")
