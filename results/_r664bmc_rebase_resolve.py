# -*- coding: utf-8 -*-
"""r664 bm-c rebase-conflict resolver receipt (6 UU vs bm-a r813 takeover tree).

Sides (REBASE direction pit r648: stage2 'ours' = upstream = bm-a r813
takeover tree; stage3 'theirs' = MY r664 round commit being replayed):
  1. results/x2_watch_log.jsonl        -> LINE UNION (append-only ledger law:
         base 833 + bma-takeover +6 (08:0x) + bmc-QA +6 (08:21:10 family),
         byte-exact dedup, order preserved)
  2. results/lhb_update_status.json   -> STAGE 2 (bm-a = LHB lane host real
         fetched face 'no events beyond cutoff'; mine = derivative
         min-interval guard state on non-host -- lane-owner-wins, R31 family)
  3. results/compute_audit.json       -> ROW UNION (own-row law, bm-b r798
         heal precedent: keep bm-a cleanup of dead-session row + restored
         rows + my r663 08:00:57 row (already in bma tree via pull) + append
         my r664 08:19:49 row; latest = newest ts = mine)
  4. results/_attrition_guard_scan.json -> STAGE 3 (mine 08:23:26 newer than
         bma 08:14:51; transient per-scan evidence face, newer-wins)
  5-6. docs/daily_report/REPORT-2026-10-07.{json,md} -> STAGE 3 (mine
         generated_at 08:21:29 > bma 08:02:51; no host guard on daily_report,
         same-day idempotent last-writer-wins)

All blob IO byte-exact (LF preserved for jsonl); JSON re-dump uses the
file-native indent style read from the stage2 blob. Zero hand-edited content.
"""
import json
import subprocess
import sys

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                        capture_output=True)
    if r.returncode != 0:
        raise SystemExit("blob read fail stage %d %s: %s" % (stage, path, r.stderr))
    return r.stdout

def resolve(path, side):
    """side: 'stage2' | 'stage3' -> checkout that stage's blob verbatim."""
    data = blob(2 if side == "stage2" else 3, path)
    with open(path, "wb") as fh:
        fh.write(data)
    print("RESOLVED %-46s <- %s (%d bytes)" % (path, side, len(data)))

def union_lines(path):
    base = blob(1, path).split(b"\n")
    s2 = blob(2, path).split(b"\n")
    s3 = blob(3, path).split(b"\n")
    # drop trailing empty artifact from split, re-add at end
    trail = base[-1] == b""
    if trail:
        base, s2, s3 = base[:-1], s2[:-1], s3[:-1]
    base_set = set(base)
    s2_new = [l for l in s2 if l not in base_set]
    seen = base_set | set(s2_new)
    s3_new = [l for l in s3 if l not in seen]
    out = base + s2_new + s3_new
    data = b"\n".join(out) + (b"\n" if trail else b"")
    with open(path, "wb") as fh:
        fh.write(data)
    dup_s3_in_s2 = len([l for l in s3 if l in set(s2_new)])
    print("RESOLVED %-46s <- UNION (base %d + s2new %d + s3new %d = %d lines, s3-dup-in-s2 %d)"
          % (path, len(base), len(s2_new), len(s3_new), len(out), dup_s3_in_s2))

def union_rows(path):
    b2 = blob(2, path)
    b3 = blob(3, path)
    d2 = json.loads(b2)
    d3 = json.loads(b3)
    rows2 = d2["history"]
    rows3 = d3["history"]
    keys2 = {json.dumps(r, sort_keys=True) for r in rows2}
    added = [r for r in rows3 if json.dumps(r, sort_keys=True) not in keys2]
    merged = rows2 + added
    latest = d3["latest"] if str(d3["latest"].get("ts", "")) > str(d2["latest"].get("ts", "")) else d2["latest"]
    out = {"latest": latest, "history": merged}
    # file-native style: detect indent from stage2 blob (json.dump indent=1 default of this repo face)
    indent = 1
    try:
        first_nl = b2.split(b"\n", 2)[1]
        indent = len(first_nl) - len(first_nl.lstrip())
    except Exception:
        pass
    text = json.dumps(out, ensure_ascii=False, indent=indent) + "\n"
    with open(path, "wb") as fh:
        fh.write(text.encode("utf-8"))
    print("RESOLVED %-46s <- ROW-UNION (s2 %d + s3-new %d = %d rows, latest ts %s, indent %d)"
          % (path, len(rows2), len(added), len(merged), str(latest.get("ts")), indent))

P_X2 = "results/x2_watch_log.jsonl"
P_LHB = "results/lhb_update_status.json"
P_CA = "results/compute_audit.json"
P_ATTR = "results/_attrition_guard_scan.json"
P_RJ = "docs/daily_report/REPORT-2026-10-07.json"
P_RM = "docs/daily_report/REPORT-2026-10-07.md"

union_lines(P_X2)
resolve(P_LHB, "stage2")
union_rows(P_CA)
resolve(P_ATTR, "stage3")
resolve(P_RJ, "stage3")
resolve(P_RM, "stage3")
print("ALL 6 UU RESOLVED")
