# -*- coding: utf-8 -*-
"""r846 bm-a rebase-UU resolver vs bm-c claim-refresh wave (11 UU).
Canon classification per r819/r825/r827/r829/r832 bloodline:
- union faces (ts-key rolling ledger): compute_audit.json, token_usage.json -> :2:+:3: union
- pool face: runnable_pool.json -> per-shard ts-field max-merge newer-wins (MSG-0612)
- snapshot faces: _attrition_guard_scan.json -> fresher generated ts whole-side
- S6 regen twins (REPORT/LIVE json+md): whole-side fresher-wins (t29 deep-ts law)
Rebase stage labels: :2: = base (origin/new), :3: = mine (replayed)."""
import json, re, subprocess, sys

def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout.decode("utf-8", errors="replace")

def stage_out(path, content):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)

def union_json(path):
    a = json.loads(blob(":2:" + path))   # origin side
    b = json.loads(blob(":3:" + path))    # mine side
    ha, hb = a.get("history", []), b.get("history", [])
    seen = {}
    for row in ha + hb:
        ts = row.get("ts", "")
        if ts not in seen:
            seen[ts] = row
    merged = [seen[k] for k in sorted(seen.keys())]
    winner = a if (ha[-1].get("ts", "") if ha else "") >= (hb[-1].get("ts", "") if hb else "") else b
    out = dict(winner)
    out["history"] = merged
    stage_out(path, json.dumps(out, ensure_ascii=False, indent=1))
    print("UNION %s: %d+%d -> %d zero-loss" % (path, len(ha), len(hb), len(merged)))

def max_merge_pool(path):
    a = json.loads(blob(":2:" + path))   # origin (bm-c claim-refresh, newest)
    b = json.loads(blob(":3:" + path))    # mine (22:30 healed)
    a_by = {e.get("id"): e for e in a.get("entries", [])}
    healed = 0
    for eid, me in b.get("entries", []).items() if isinstance(b.get("entries"), dict) else []:
        pass
    ent = b.get("entries", [])
    a_by = {e.get("id"): e for e in a.get("entries", [])}
    for me in ent:
        oe = a_by.get(me.get("id"))
        if not oe:
            continue
        osh = {s.get("key"): s for s in oe.get("shards", [])}
        for ms in me.get("shards", []):
            os_ = osh.get(ms.get("key"))
            if not os_:
                continue
            for f in ("owner_since", "cleared_ts", "claimed_at", "done_at"):
                ov, mv = os_.get(f), ms.get(f)
                if ov and (not mv or ov > mv):
                    ms[f] = ov
                    if f == "owner_since":
                        ms["owner"] = os_.get("owner", ms.get("owner"))
                    healed += 1
    stage_out(path, json.dumps(b, ensure_ascii=False, indent=1))
    print("POOL-MAXMERGE %s: %d shard ts fields forward-kept" % (path, healed))

def snapshot_fresher(path):
    a = blob(":2:" + path)
    b = blob(":3:" + path)
    def genn(s):
        m = re.search(r'"generated[^"]*":\s*"([^"]+)"', s)
        return m.group(1) if m else ""
    ga, gb = genn(a), genn(b)
    winner = a if ga >= gb else b
    stage_out(path, winner)
    print("SNAPSHOT %s: origin=%s mine=%s -> %s" % (path, ga, gb, "origin(:2:)" if ga >= gb else "mine(:3:)"))

def twin_fresher(path):
    a = blob(":2:" + path)
    b = blob(":3:" + path)
    def genn(s):
        m = re.search(r'"generated[^"]*":\s*"([^"]+)"', s)
        if not m:
            m = re.search(r'generated[":\s]+([0-9T:\-+.]+)', s)
        return m.group(1) if m else ""
    ga, gb = genn(a), genn(b)
    winner = a if ga >= gb else b
    stage_out(path, winner)
    print("TWIN %s: origin=%s mine=%s -> %s" % (path, ga or "?", gb or "?", "origin(:2:)" if ga >= gb else "mine(:3:)"))

for p in ["results/compute_audit.json", "results/token_usage.json"]:
    union_json(p)
max_merge_pool("results/runnable_pool.json")
snapshot_fresher("results/_attrition_guard_scan.json")
for p in ["docs/daily_report/REPORT-2026-10-07.json", "docs/daily_report/REPORT-2026-10-07.md",
          "docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
    twin_fresher(p)
print("ALL RESOLVED")
